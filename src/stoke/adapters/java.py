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
from stoke.config import Target, ProjectInfo
from stoke.java_versions import (
    JavaInstall,
    detect_all,
    find_matching,
)
from stoke.lock import LockFile, load_lock, save_lock


@dataclass
class CompileResult:
    ok: bool
    error: str = ""


class JavaAdapter(BaseAdapter):
    def __init__(
        self,
        target: Target,
        project: ProjectInfo,
        project_root: Path,
    ):
        super().__init__(target, project, project_root)
        self.classes_dir = project_root / ".stoke" / "classes" / target.name

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
            install = find_matching(str(lock.java.major_version))
            if install is None:
                available = detect_all()
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
            install = find_matching(self.target.java_version)
            if install is None:
                available = detect_all()
                available_versions = ", ".join(str(i.major_version) for i in available)
                raise RuntimeError(
                    f"Java {self.target.java_version} not found on this system.\n"
                    f"  Available versions: {available_versions or '(none)'}\n"
                    f"  Install JDK {self.target.java_version} or update java_version in stoke.toml."
                )
            return install

        # stoke.toml에도 없으면 시스템 default
        installs = detect_all()
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
        # -cp: 클래스패스 (기존 classes 폴더도 포함해서 이전 컴파일 결과 참조 가능)
        cmd = [
            str(jdk.javac),
            "-d", str(self.classes_dir),
            "-cp", str(self.classes_dir),
        ] + [str(f) for f in files_to_compile]

        proc = subprocess.run(cmd, capture_output=True, text=True)

        if proc.returncode == 0:
            # 성공: 모든 파일 캐시 갱신
            for file in files_to_compile:
                file_key = str(file.relative_to(self.project_root))
                target_cache.syntax_check[file_key] = get_file_stat(file)
                results.append(CompileResult(ok=True))
            for _ in skipped:
                results.append(CompileResult(ok=True))
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

    def build(self, force: bool = False) -> None:
        jdk, should_update_lock = self.resolve_jdk()
        lock = load_lock(self.project_root, self.project.lock_mode)
        cache = load_cache(self.project_root)

        print(f"Using JDK {jdk.version} (major: {jdk.major_version})")
        print(f"  JAVA_HOME: {jdk.java_home}")

        # 소스 수집
        print("\n--- Collecting sources ---")
        source_files = self.collect_source_files()
        if not source_files:
            print("No source files found matching sources patterns")
            self._ensure_gitignore()
            return

        print(f"Found {len(source_files)} source file(s)")

        # 컴파일
        print("\n--- Compiling ---")
        results, skipped = self.compile_all(jdk, source_files, cache, force=force)

        failed = [r for r in results if not r.ok]

        if skipped:
            print(f"  Skipped {len(skipped)} unchanged file(s)")

        newly_compiled = len(source_files) - len(skipped)
        if newly_compiled > 0 and not failed:
            print(f"  Compiled {newly_compiled} file(s)")

        if failed:
            # 컴파일 에러는 하나만 나오면 그거 그대로 출력 (javac 출력이 이미 다 담고 있음)
            print("\nCompilation failed:")
            print(failed[0].error)

            save_cache(self.project_root, cache)
            self._ensure_gitignore()
            raise RuntimeError(
                f"Compilation failed: {len(failed)} of {len(results)} files"
            )

        # lock 파일 저장
        need_save_lock = should_update_lock or (
            lock is None or lock.java is None
        )
        if need_save_lock:
            lock_path = save_lock(
                self.project_root,
                self.project.lock_mode,
                java_version=jdk.version,
                java_major_version=jdk.major_version,
                java_home=str(jdk.java_home),
            )
            print(f"\nLock file saved: {lock_path}")

        # 캐시 저장
        save_cache(self.project_root, cache)

        # .gitignore 관리
        self._ensure_gitignore()

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
            "-cp", str(self.classes_dir),
            self.target.main_class,
        ]

        print(f"Running: {self.target.main_class}\n")
        result = subprocess.run(cmd)
        return result.returncode

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
            "-cp", str(self.classes_dir),
            self.target.main_class,
        ]