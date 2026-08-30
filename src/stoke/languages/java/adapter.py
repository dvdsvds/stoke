import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

from stoke.adapters.base import BaseAdapter
from stoke.cache import (
    BuildCache,
    load_cache,
    save_cache,
    get_file_stat,
    is_unchanged,
)
from stoke import remote_cache
from stoke.config import Target, ProjectInfo
from stoke.languages.java.versions import (
    JavaInstall,
    detect_all,
    find_matching,
)
from stoke.lock import load_lock, save_lock, JavaDep, JavaLock

@dataclass
class CompileResult:
    ok: bool
    error: str = ""
    from_remote_cache: bool = False

class JavaAdapter(BaseAdapter):
    def __init__(
        self,
        target: Target,
        project: ProjectInfo,
        project_root: Path,
        verbose: bool = False,
    ):
        super().__init__(target, project, project_root, verbose=verbose)
        self.lang_dir = project_root / ".stoke" / "java" / target.name
        self.classes_dir = self.lang_dir / "classes"
        self.deps_dir = self.lang_dir / "deps"

    def resolve_jdk(self) -> tuple[JavaInstall, bool]:
        """
        어떤 JDK를 쓸지 결정.
        반환: (JavaInstall, lock을 갱신해야 하는지 여부)
        """
        lock = load_lock(self.project_root, self.project.lock_mode)

        # 1. lock 파일에 자바 정보 있으면 우선 사용
        if lock is not None and lock.java is not None:
            # stoke.toml 요청 버전이랑 호환되는지
            if self.target.java_version:
                # 메이저 버전만 비교 (예: "21" -> 21)
                try:
                    requested_major = int(self.target.java_version.split(".")[0])
                    if lock.java.major_version != requested_major:
                        print(
                            f"stoke.toml requests Java {self.target.java_version} "
                            f"but lock file has Java {lock.java.version}. Updating lock."
                        )
                        return self._resolve_from_stoke_toml(), True
                except ValueError:
                    pass

            # lock 버전으로 시스템에서 찾기
            install = find_matching(str(lock.java.major_version), self.project_root)
            if install is None:
                available = detect_all(self.project_root)
                available_versions = ", ".join(str(i.major_version) for i in available)
                raise RuntimeError(
                    f"Lock file requires Java {lock.java.version}, but it's not installed on this system.\n"
                    f"  Available versions: {available_versions or '(none)'}\n"
                    f"  Options:\n"
                    f"    1. Install JDK {lock.java.major_version} on this system\n"
                    f"    2. Delete the lock file to regenerate\n"
                    f"    3. Change java_version in stoke.toml to a compatible version"
                )
            return install, False

        # 2. lock 없거나 자바 정보 없으면 stoke.toml 기준
        return self._resolve_from_stoke_toml(), True

    def _resolve_from_stoke_toml(self) -> JavaInstall:
        """stoke.toml 기준으로 JDK 결정."""
        if self.target.java_version:
            install = find_matching(self.target.java_version, self.project_root)
            if install is None:
                available = detect_all(self.project_root)
                available_versions = ", ".join(str(i.major_version) for i in available)
                raise RuntimeError(
                    f"Java {self.target.java_version} not found on this system.\n"
                    f"  Available versions: {available_versions or '(none)'}\n"
                    f"  Install JDK {self.target.java_version} or update java_version in stoke.toml.\n"
                    f"  (stoke install --language=java --version={self.target.java_version})"
                )
            return install

        # stoke.toml에도 없으면 시스템 default
        installs = detect_all(self.project_root)
        if not installs:
            raise RuntimeError(
                "No JDK detected on this system.\n"
                "  Install a JDK or set the JAVA_HOME environment variable."
            )

        for install in installs:
            if install.is_default:
                return install
        return installs[0]

    def collect_source_files(self) -> list[Path]:
        """sources 패턴에서 .java 파일 목록 수집."""
        collected = []
        seen = set()

        for pattern in self.target.sources:
            matched = list(self.project_root.glob(pattern))
            for path in matched:
                if not path.is_file():
                    continue
                if path.suffix != ".java":
                    continue
                # .stoke 폴더 제외
                try:
                    path.relative_to(self.project_root / ".stoke")
                    continue
                except ValueError:
                    pass

                real = path.resolve()
                if real in seen:
                    continue
                seen.add(real)
                collected.append(path)

        return sorted(collected)

    def _source_dirs(self) -> list[Path]:
        """
        sources 패턴에서 소스 최상위 폴더 추출.
        예: ["src/**/*.java"] -> [project_root/src]
        """
        roots = set()
        for pattern in self.target.sources:
            parts = Path(pattern).parts
            root_parts = []
            for part in parts:
                if any(ch in part for ch in ("*", "?", "[")):
                    break
                root_parts.append(part)

            if not root_parts:
                roots.add(self.project_root)
            else:
                root = self.project_root / Path(*root_parts)
                if root.is_file():
                    root = root.parent
                roots.add(root)

        return sorted(r for r in roots if r.exists())

    def _generate_ide_files(self) -> None:
        """
        Eclipse/VSCode Java 확장용 .classpath, .project 파일 생성.
        VSCode용 .vscode/settings.json도 생성.
        IntelliJ 등을 위한 pom.xml도 생성.
        빌드 성공 후에만 호출.
        """
        from stoke.ide.java_eclipse import write_ide_files
        from stoke.ide.vscode import write_project_settings, make_java_settings
        from stoke.ide.maven import write_pom

        source_dirs = self._source_dirs()
        if not source_dirs:
            return
        jar_files = self._existing_jars()

        ## Eclipse 형식 (.classpath, .project)
        _, _, classpath_changed, project_changed = write_ide_files(
            project_root=self.project_root,
            project_name=self.target.name,
            source_dirs=source_dirs,
            output_dir=self.classes_dir,
            jar_files=jar_files,
        )

        # VSCode 설정 (.vscode/settings.json)
        java_settings = make_java_settings(jar_files, self.project_root)
        _, settings_changed = write_project_settings(self.project_root, java_settings)

        # Maven pom.xml (IntelliJ 등)
        java_version = str(self.target.java_version or "25")
        _, pom_changed = write_pom(
            project_root=self.project_root,
            project_name=self.target.name,
            project_version=self.project.version or "0.1.0",
            java_version=java_version,
            source_dirs=source_dirs,
            output_dir=self.classes_dir,
            deps=self.target.deps or {},
        )

        # 변경된 파일만 알림
        changed_files = []
        if classpath_changed:
            changed_files.append(".classpath")
        if project_changed:
            changed_files.append(".project")
        if settings_changed:
            changed_files.append(".vscode/settings.json")
        if pom_changed:
            changed_files.append("pom.xml")
        if changed_files:
            print(f"IDE files updated: {', '.join(changed_files)}")
        
    def _target_fingerprint(self, jdk: JavaInstall, files: list[Path]) -> str:
        """
        타겟 전체 소스 세트 기준 원격 캐시 fingerprint.
        C/C++처럼 파일 하나당 하나가 아니라, javac가 변경분을 한 번에 몰아서
        컴파일하는 구조에 맞춰 "이 타겟을 이루는 소스 파일 전체의 내용"을
        통째로 반영함 — 파일 하나라도 내용이 바뀌면 값이 통째로 바뀜.
        """
        parts = []
        for file in sorted(files, key=lambda f: str(f)):
            file_key = str(file.relative_to(self.project_root))
            parts.append(f"{file_key}:{get_file_stat(file).content_hash}")
        compiler_id = f"java-{jdk.version}"
        # 의존성(클래스패스) 구성이 다르면 다른 캐시로 취급
        deps_id = json.dumps(dict(sorted((self.target.deps or {}).items())))
        return remote_cache.compute_fingerprint("|".join(parts), compiler_id, [deps_id])

    def compile_all(
        self,
        jdk: JavaInstall,
        files: list[Path],
        cache: BuildCache,
        force: bool = False,
    ) -> tuple[list[CompileResult], list[Path]]:
        """
        전체 파일 컴파일.
        캐시로 skip 판단은 하지만, 실제 javac 호출은 변경된 파일들만 함.
        반환: (결과 리스트, skip된 파일 리스트)
        """
        target_cache = cache.get_target(self.target.name)
        # syntax_check 캐시를 재사용 (자바에선 컴파일 완료 표시 용도)
        # 파이썬이랑 필드 이름 공유해서 구조 유지

        # 원격 캐시 확인: 소스 전체 세트가 이전에 컴파일된 적 있으면
        # javac 호출 자체를 생략하고 classes_dir을 통째로 받아옴
        # (새 체크아웃/CI처럼 로컬 캐시가 비어있어 모든 파일이 대상일 때 특히 유효)
        remote_dir = remote_cache.get_remote_cache_dir()
        fingerprint = None
        if remote_dir is not None:
            fingerprint = self._target_fingerprint(jdk, files)
            if not force and remote_cache.try_fetch_dir(remote_dir, fingerprint, self.classes_dir):
                results = []
                for file in files:
                    file_key = str(file.relative_to(self.project_root))
                    target_cache.syntax_check[file_key] = get_file_stat(file)
                    results.append(CompileResult(ok=True, from_remote_cache=True))
                return results, []

        # skip 판단
        files_to_compile = []
        skipped = []

        for file in files:
            file_key = str(file.relative_to(self.project_root))
            current_stat = get_file_stat(file)

            if not force:
                cached_stat = target_cache.syntax_check.get(file_key)
                if cached_stat is not None and is_unchanged(current_stat, cached_stat):
                    # 클래스 파일이 실제로 존재하는지도 확인해야 안전
                    # 근데 자바는 소스 → 클래스 매핑이 복잡 (패키지 구조 반영)
                    # 일단은 mtime만 보고 skip
                    skipped.append(file)
                    continue

            files_to_compile.append(file)

        results = []

        if not files_to_compile:
            # 다 skip
            for f in files:
                results.append(CompileResult(ok=True))
            return results, skipped

        # 출력 폴더 준비
        self.classes_dir.mkdir(parents=True, exist_ok=True)

        # javac 실행
        # -d: 출력 폴더
        # -cp: 클래스패스 (classes_dir + deps_dir의 JAR들)
        cmd = [
            str(jdk.javac),
            "-J-Dfile.encoding=UTF-8",
            "-J-Dstdout.encoding=UTF-8",
            "-J-Dstderr.encoding=UTF-8",
            "-encoding", "UTF-8",
            "-d", str(self.classes_dir),
            "-cp", self._classpath(),
        ] + [str(f) for f in files_to_compile]
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        if proc.returncode == 0:
            # 성공: 모든 파일 캐시 갱신
            for file in files_to_compile:
                file_key = str(file.relative_to(self.project_root))
                target_cache.syntax_check[file_key] = get_file_stat(file)
                results.append(CompileResult(ok=True))
            for _ in skipped:
                results.append(CompileResult(ok=True))

            if remote_dir is not None:
                remote_cache.store_dir(remote_dir, fingerprint, self.classes_dir)
        else:
            # 실패: 에러 메시지는 stderr에
            error_msg = proc.stderr.strip() or proc.stdout.strip()
            # 컴파일 실패 파일들은 캐시에서 제거
            for file in files_to_compile:
                file_key = str(file.relative_to(self.project_root))
                target_cache.syntax_check.pop(file_key, None)
                results.append(CompileResult(ok=False, error=error_msg))
            for _ in skipped:
                results.append(CompileResult(ok=True))

        return results, skipped

    def install_deps(self) -> dict[str, dict]:
        """
        stoke.toml의 deps를 Maven Central에서 다운로드.
        반환: {name: {"version": str, "sha1": str, "path": Path}}
        """
        import hashlib
        from stoke.languages.java.maven import parse_coordinate, download_jar

        if not self.target.deps:
            return {}

        print(f"Installing {len(self.target.deps)} dependency(ies)...")

        installed = {}
        for name, version in self.target.deps.items():
            try:
                coord = parse_coordinate(name, version)
                jar_path = download_jar(coord, self.deps_dir)
                # SHA-1 계산 (다운로드된 파일 기준)
                sha1 = hashlib.sha1(jar_path.read_bytes()).hexdigest()
                installed[name] = {
                    "version": version,
                    "sha1": sha1,
                    "path": jar_path,
                }
            except (ValueError, RuntimeError) as e:
                raise RuntimeError(f"Failed to install {name}:{version}\n  {e}")

        print(f"  Installed {len(installed)} JAR(s)")
        return installed

    def _existing_jars(self) -> list[Path]:
        """이미 deps_dir에 있는 JAR 파일들."""
        if not self.deps_dir.exists():
            return []
        return sorted(self.deps_dir.glob("*.jar"))

    def _deps_changed(self, lock, installed_deps: dict[str, dict]) -> bool:
        """
        현재 설치된 의존성이 lock 파일과 다른지 확인.
        다르면 True (lock 갱신 필요), 같으면 False (skip).
        """
        if lock is None or not lock.java_deps:
            return bool(installed_deps)

        if set(lock.java_deps.keys()) != set(installed_deps.keys()):
            return True

        for name, info in installed_deps.items():
            lock_dep = lock.java_deps[name]
            if lock_dep.version != info["version"]:
                return True
            if lock_dep.sha1 != info["sha1"]:
                return True

        return False

    def _classpath(self) -> str:
        """
        컴파일/실행에 사용할 클래스패스.
        classes_dir + deps_dir 안의 모든 JAR.
        Windows는 세미콜론, 리눅스/맥은 콜론 구분자.
        """
        import os
        separator = os.pathsep
        parts = [str(self.classes_dir)]
        for jar in self._existing_jars():
            parts.append(str(jar))
        return separator.join(parts)
    
    def build(self, force: bool = False) -> None:
        jdk, should_update_lock = self.resolve_jdk()
        lock = load_lock(self.project_root, self.project.lock_mode)
        cache = load_cache(self.project_root)
        print(f"Using JDK {jdk.version} (major: {jdk.major_version})")
        if self.verbose:
            print(f"  JAVA_HOME: {jdk.java_home}")
        # 의존성 설치
        installed_deps = {}
        if self.target.deps:
            if self.verbose:
                print("\n--- Installing dependencies ---")
            try:
                installed_deps = self.install_deps()
            except RuntimeError as e:
                self._ensure_gitignore()
                raise
        # 소스 수집
        if self.verbose:
            print("\n--- Collecting sources ---")
        source_files = self.collect_source_files()
        if self.verbose:
            print(f"Found {len(source_files)} source file(s)")
        # 컴파일
        if self.verbose:
            print("\n--- Compiling ---")
        results, skipped = self.compile_all(jdk, source_files, cache, force=force)
        failed = [r for r in results if not r.ok]
        remote_cache_hits = sum(1 for r in results if r.ok and r.from_remote_cache)
        newly_compiled = len(source_files) - len(skipped) - remote_cache_hits
        # 요약: 통합 표시
        if not failed:
            parts = []
            if newly_compiled > 0:
                parts.append(f"Compiled {newly_compiled} file(s)")
            if remote_cache_hits > 0:
                parts.append(f"Remote cache hit for {remote_cache_hits} file(s)")
            if skipped:
                parts.append(f"Skipped {len(skipped)} unchanged file(s)")
            if parts:
                print(", ".join(parts))

        if failed:
            # 컴파일 에러는 하나만 나오면 그거 그대로 출력 (javac 출력이 이미 다 담고 있음)
            print("\nCompilation failed:")
            print(failed[0].error)

            save_cache(self.project_root, cache)
            self._ensure_gitignore()
            raise RuntimeError(
                f"Compilation failed: {len(failed)} of {len(results)} files"
            )

        # lock 파일 저장 (실제 변경 있을 때만)
        from stoke.lock import JavaDep
        java_deps_for_lock = {}
        for name, info in installed_deps.items():
            java_deps_for_lock[name] = JavaDep(
                version=info["version"],
                sha1=info["sha1"],
            )
        lock_path, lock_changed = save_lock(
            self.project_root,
            self.project.lock_mode,
            java=JavaLock(version=jdk.version, major_version=jdk.major_version, java_home=str(jdk.java_home)),
            java_deps=java_deps_for_lock,
        )
        if lock_changed:
            print(f"Lock file saved: {lock_path}")

        # 캐시 저장
        save_cache(self.project_root, cache)
        # .gitignore 관리
        self._ensure_gitignore()
        # IDE 통합 파일 생성
        self._generate_ide_files()
        print(f"\nBuild complete: {self.target.name}")

    def run(self) -> int:
        """
        컴파일된 클래스를 실행.
        반환: 종료 코드
        """
        if not self.target.main_class:
            raise RuntimeError(
                f"Target '{self.target.name}' has no 'main_class' field in stoke.toml.\n"
                f"  Add 'main_class = \"com.example.Main\"' under [targets.{self.target.name}]"
            )

        if not self.classes_dir.exists():
            raise RuntimeError(
                f"Classes directory not found: {self.classes_dir}\n"
                f"  Run 'stoke build' first." 
            )

        jdk, _ = self.resolve_jdk()

        cmd = [
            str(jdk.java),
            "-cp", self._classpath(),
            self.target.main_class,
        ]

        print(f"Running: {self.target.main_class}\n")
        try:
            result = subprocess.run(cmd)
            return result.returncode
        except KeyboardInterrupt:
            return 130

    def get_run_command(self) -> list[str]:
        """hot-reload용 실행 명령어."""
        if not self.target.main_class:
            raise RuntimeError(
                f"Target '{self.target.name}' has no 'main_class' field in stoke.toml.\n"
                f"  Add 'main_class = \"com.example.Main\"' under [targets.{self.target.name}]"
            )

        if not self.classes_dir.exists():
            raise RuntimeError(
                f"Classes directory not found: {self.classes_dir}\n"
                f"  Run 'stoke build' first."
            )

        jdk, _ = self.resolve_jdk()

        return [
            str(jdk.java),
            "-cp", self._classpath(),
            self.target.main_class,
        ]

    # JUnit Platform Console Standalone -- 하나의 jar에 JUnit Jupiter API/엔진까지 다 들어있어서
    # 이거 하나만 받으면 별도 의존성 없이 컴파일+실행 둘 다 됨.
    _JUNIT_CONSOLE_VERSION = "1.11.3"

    def _junit_console_jar(self) -> Path:
        """JUnit Platform Console Standalone jar 다운로드(캐시되면 재사용)해서 경로 반환."""
        from stoke.languages.java.maven import MavenCoordinate, download_jar

        coord = MavenCoordinate(
            group_id="org.junit.platform",
            artifact_id="junit-platform-console-standalone",
            version=self._JUNIT_CONSOLE_VERSION,
        )
        return download_jar(coord, self.lang_dir / "test-deps")

    def _collect_test_files(self) -> list[Path]:
        """test_sources 패턴에서 .java 파일 목록 수집 (collect_source_files와 동일한 규칙)."""
        collected = []
        seen = set()
        for pattern in self.target.test_sources:
            for path in self.project_root.glob(pattern):
                if not path.is_file() or path.suffix != ".java":
                    continue
                try:
                    path.relative_to(self.project_root / ".stoke")
                    continue
                except ValueError:
                    pass
                real = path.resolve()
                if real in seen:
                    continue
                seen.add(real)
                collected.append(path)
        return sorted(collected)

    def test(self, verbose: bool = False) -> int:
        """
        test_sources를 JUnit 5(JUnit Jupiter)로 컴파일+실행.
        JUnit Platform Console Standalone jar를 최초 1회 Maven Central에서 받아서 씀
        (org.junit.jupiter.api.Test 등을 그대로 씀 -- 별도 stoke 전용 assertion 문법 없음).
        """
        import os

        if not self.target.test_sources:
            raise RuntimeError(
                "No 'test_sources' configured for this target in stoke.toml.\n"
                f"  Add e.g. test_sources = [\"src/test/**/*.java\"] under [targets.{self.target.name}]"
            )
        if not self.classes_dir.exists():
            raise RuntimeError(
                f"Classes directory not found: {self.classes_dir}\n"
                f"  Run 'stoke build' first."
            )

        test_files = self._collect_test_files()
        if not test_files:
            raise RuntimeError(
                f"No test files found matching test_sources patterns: {self.target.test_sources}"
            )

        jdk, _ = self.resolve_jdk()
        junit_jar = self._junit_console_jar()

        test_classes_dir = self.lang_dir / "test-classes"
        test_classes_dir.mkdir(parents=True, exist_ok=True)

        print(f"Compiling {len(test_files)} test file(s)...")
        compile_cmd = [
            str(jdk.javac),
            "-encoding", "UTF-8",
            "-d", str(test_classes_dir),
            "-cp", os.pathsep.join([self._classpath(), str(junit_jar)]),
        ] + [str(f) for f in test_files]
        proc = subprocess.run(compile_cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if proc.returncode != 0:
            raise RuntimeError(f"Test compilation failed:\n{proc.stderr.strip() or proc.stdout.strip()}")

        run_cmd = [str(jdk.java), "-jar", str(junit_jar), "execute", "--disable-banner"]
        for entry in (self._classpath(), str(test_classes_dir)):
            run_cmd += ["--classpath", entry]
        run_cmd += ["--scan-classpath", str(test_classes_dir)]
        if verbose:
            run_cmd.append("--details=verbose")

        print(f"Running: JUnit tests in {test_classes_dir}\n")
        try:
            result = subprocess.run(run_cmd)
            return result.returncode
        except KeyboardInterrupt:
            return 130