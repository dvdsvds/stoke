import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
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
from stoke.c_versions import CompilerInstall, find_compiler
from stoke.config import Target, ProjectInfo, Profile
from stoke.lock import load_lock, save_lock
from stoke.adapters.c_dep_parser import parse_dep_file

@dataclass
class CompileResult:
    ok: bool
    error: str = ""

class CBaseAdapter(BaseAdapter):
    compiler_kind: str = ""       # 서브클래스에서 오버라이드
    source_extension: str = ""    # 서브클래스에서 오버라이드
    default_standard: str = ""    # 서브클래스에서 오버라이드
    standard_flag_prefix: str = "-std="  # gcc/g++ 공통

    def __init__(
        self,
        target: Target,
        project: ProjectInfo,
        project_root: Path,
        profile: Profile | None = None,
        verbose: bool = False,
    ):
        super().__init__(target, project, project_root, verbose=verbose)
        self.profile = profile

        # 프로파일별 폴더 분리
        profile_name = profile.name if profile else "default"
        self.lang_dir = project_root / ".stoke" / self.compiler_kind / target.name / profile_name
        self.objects_dir = self.lang_dir / "objects"
        self.output_path = self.lang_dir / self._executable_name()

    def _executable_name(self) -> str:
        """실행 파일 이름. Windows는 .exe 추가."""
        import platform
        if platform.system() == "Windows":
            return f"{self.target.name}.exe"
        return self.target.name

    def _get_standard(self) -> str | None:
        """stoke.toml에서 지정한 표준 또는 None (컴파일러 기본값 사용)."""
        # 서브클래스가 오버라이드
        return None

    def resolve_compiler(self) -> CompilerInstall:
        """
        어떤 컴파일러를 쓸지 결정.
        프로파일의 compiler 필드가 있으면 그걸 사용, 없으면 기본값 (gcc).
        """
        # 프로파일이 특정 컴파일러 요구하면 그거 사용
        compiler_family = "gcc"
        if self.profile and self.profile.compiler:
            compiler_family = self.profile.compiler

        install = find_compiler(self.compiler_kind, compiler_family=compiler_family)
        if install is None:
            profile_note = f" (required by profile '{self.profile.name}')" if self.profile and self.profile.compiler else ""
            raise RuntimeError(
                f"No {self.compiler_kind} compiler ({compiler_family}) detected{profile_note}.\n"
                f"  Install {compiler_family} or ensure it's in your PATH."
            )
        return install

    def collect_source_files(self) -> list[Path]:
        """sources 패턴에서 소스 파일 목록 수집."""
        collected = []
        seen = set()

        for pattern in self.target.sources:
            matched = list(self.project_root.glob(pattern))
            for path in matched:
                if not path.is_file():
                    continue
                if path.suffix != self.source_extension:
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
        """sources 패턴에서 소스 최상위 폴더 추출."""
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

    def _include_dirs(self) -> list[Path]:
        """
        Include 경로 자동 수집.
        - 소스 폴더 (헤더 함께 있는 경우 대비)
        - 프로젝트 루트의 include/ 폴더
        - stoke.toml의 includes 필드에 명시된 것
        """
        includes = []

        # 소스 폴더
        for src_dir in self._source_dirs():
            includes.append(src_dir)

        # 프로젝트 루트의 include/
        default_include = self.project_root / "include"
        if default_include.is_dir():
            includes.append(default_include)

        # 사용자 명시
        for path_str in self.target.includes:
            path = self.project_root / path_str
            if path.is_dir():
                includes.append(path)
        
        # vcpkg include 경로 (deps 있으면)
        if self.target.deps:
            from stoke.vcpkg import get_include_dir, is_vcpkg_installed
            if is_vcpkg_installed():
                vcpkg_include = get_include_dir()
                if vcpkg_include.is_dir():
                    includes.append(vcpkg_include)

        # 중복 제거하고 정렬
        seen = set()
        unique = []
        for path in includes:
            resolved = path.resolve()
            if resolved not in seen:
                seen.add(resolved)
                unique.append(path)
        return unique

    def _object_path(self, source: Path) -> Path:
        """
        소스 파일에 대응하는 .o 파일 경로.
        src/foo/bar.c -> .stoke/{kind}/{target}/objects/src/foo/bar.o
        """
        try:
            rel = source.relative_to(self.project_root)
        except ValueError:
            rel = Path(source.name)
        obj_path = self.objects_dir / rel.with_suffix(".o")
        return obj_path

    def _compile_one(
        self,
        compiler: "CompilerInstall",
        file: Path,
    ) -> tuple[Path, "CompileResult", dict]:
        """
        파일 하나 컴파일. 병렬 실행 대상.

        반환: (파일, 결과, 헤더_stats)
        헤더_stats: 성공 시 {헤더경로: FileStat} 딕셔너리, 실패 시 빈 dict
        """
        obj_path = self._object_path(file)
        obj_path.parent.mkdir(parents=True, exist_ok=True)

        cmd = [str(compiler.executable)]
        # 표준 옵션
        standard = self._get_standard()
        if standard:
            cmd.append(f"{self.standard_flag_prefix}{standard}")

        # 프로파일별 컴파일 옵션
        if self.profile:
            cmd.extend(self.profile.compile_flags)
            for define in self.profile.defines:
                cmd.append(f"-D{define}")

        # Include 경로
        for include_dir in self._include_dirs():
            cmd.extend(["-I", str(include_dir)])
        # 헤더 의존성 파일 (.d) 자동 생성
        dep_path = obj_path.with_suffix(".d")
        cmd.extend(["-MD", "-MF", str(dep_path)])
        # 컴파일만 (링크 X)
        cmd.extend(["-c", str(file), "-o", str(obj_path)])

        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        if proc.returncode == 0:
            # 헤더 의존성 파싱
            headers = parse_dep_file(dep_path)
            header_stats = {}
            for header in headers:
                if header.exists():
                    header_stats[str(header)] = get_file_stat(header)
            return file, CompileResult(ok=True), header_stats
        else:
            error_msg = proc.stderr.strip() or proc.stdout.strip()
            return file, CompileResult(ok=False, error=error_msg), {}

    def compile_all(
        self,
        compiler: CompilerInstall,
        files: list[Path],
        cache: BuildCache,
        force: bool = False,
    ) -> tuple[list[CompileResult], list[Path]]:
        """
        모든 소스 파일을 오브젝트 파일로 컴파일.
        반환: (결과 리스트, skip된 파일 리스트)
        """
        target_cache = cache.get_target(self.target.name)

        files_to_compile = []
        skipped = []

        for file in files:
            file_key = str(file.relative_to(self.project_root))
            current_stat = get_file_stat(file)
            obj_path = self._object_path(file)
            if not force:
                cached_stat = target_cache.syntax_check.get(file_key)
                if cached_stat is not None and is_unchanged(current_stat, cached_stat):
                    if obj_path.exists():
                        # 헤더 파일도 변경 없는지 확인
                        cached_headers = target_cache.header_deps.get(file_key, {})
                        headers_unchanged = True
                        for header_path_str, cached_header_stat in cached_headers.items():
                            header_path = Path(header_path_str)
                            if not header_path.exists():
                                headers_unchanged = False
                                break
                            current_header_stat = get_file_stat(header_path)
                            if not is_unchanged(current_header_stat, cached_header_stat):
                                headers_unchanged = False
                                break

                        if headers_unchanged:
                            skipped.append(file)
                            continue
            files_to_compile.append(file)

        results = []
        if not files_to_compile:
            for _ in files:
                results.append(CompileResult(ok=True))
            return results, skipped

        # 워커 수 결정: stoke.toml의 jobs 우선, 없으면 CPU 코어 수
        max_workers = self.project.jobs or os.cpu_count() or 1

        # 병렬 컴파일
        total = len(files_to_compile)
        completed_count = 0
        compile_results: dict[Path, tuple] = {}  # {파일: (결과, 헤더_stats)}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {
                executor.submit(self._compile_one, compiler, file): file
                for file in files_to_compile
            }

            for future in as_completed(future_to_file):
                file, result, header_stats = future.result()
                completed_count += 1

                # 진행률 표시
                rel_path = file.relative_to(self.project_root)
                if result.ok:
                    print(f"  [{completed_count}/{total}] compiled {rel_path}")
                else:
                    print(f"  [{completed_count}/{total}] FAILED  {rel_path}")

                compile_results[file] = (result, header_stats)

        # 결과 처리 (원본 순서 유지)
        for file in files_to_compile:
            result, header_stats = compile_results[file]
            file_key = str(file.relative_to(self.project_root))

            if result.ok:
                target_cache.syntax_check[file_key] = get_file_stat(file)
                target_cache.header_deps[file_key] = header_stats
                results.append(result)
            else:
                target_cache.syntax_check.pop(file_key, None)
                results.append(result)

        # skip된 파일들
        for _ in skipped:
            results.append(CompileResult(ok=True))

        return results, skipped

    def link(self, compiler: CompilerInstall, files: list[Path]) -> None:
        """오브젝트 파일들을 링크해서 실행 파일 생성."""
        object_files = [self._object_path(f) for f in files]
        cmd = [str(compiler.executable)]
        cmd.extend([str(o) for o in object_files])
        cmd.extend(["-o", str(self.output_path)])

        # vcpkg 라이브러리 링크 (deps 있으면)
        if self.target.deps:
            from stoke.vcpkg import get_lib_dir, is_vcpkg_installed
            if is_vcpkg_installed():
                lib_dir = get_lib_dir()
                if lib_dir.is_dir():
                    cmd.append(f"-L{lib_dir}")
                    for lib_name in self.target.deps:
                        cmd.append(f"-l{lib_name}")

        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if proc.returncode != 0:
            error_msg = proc.stderr.strip() or proc.stdout.strip()
            raise RuntimeError(f"Link failed:\n{error_msg}")

    def _generate_ide_files(self, compiler: CompilerInstall, source_files: list[Path]) -> None:
        """
        C/C++ IDE 통합용 compile_commands.json 및 c_cpp_properties.json 생성.
        settings.json에 .stoke/ 감시 제외 설정 추가.
        """
        from stoke.ide.c_compile_commands import write_compile_commands
        from stoke.ide.vscode import (
            make_cpp_settings,
            write_cpp_properties,
            make_project_settings,
            write_project_settings,
        )
        
        # compile_commands.json
        _, cc_changed = write_compile_commands(
            project_root=self.project_root,
            compiler_path=compiler.executable,
            source_files=source_files,
            objects_dir=self.objects_dir,
            include_dirs=self._include_dirs(),
            standard=self._get_standard(),
            standard_flag_prefix=self.standard_flag_prefix,
        )
        # c_cpp_properties.json (VSCode C/C++ 확장이 compile_commands.json 인식하도록)
        cpp_settings = make_cpp_settings(
            language=self.compiler_kind,
            standard=self._get_standard() or "",
            compiler_path=str(compiler.executable),
        )
        _, cpp_changed = write_cpp_properties(self.project_root, cpp_settings)
        # settings.json에 .stoke/ 감시 제외 (렉 방지)
        project_settings = make_project_settings()
        _, settings_changed = write_project_settings(self.project_root, project_settings)

        # 변경된 파일만 알림
        changed_files = []
        if cc_changed:
            changed_files.append("compile_commands.json")
        if cpp_changed:
            changed_files.append(".vscode/c_cpp_properties.json")
        if settings_changed:
            changed_files.append(".vscode/settings.json")
        if changed_files:
            print(f"IDE files updated: {', '.join(changed_files)}")

    def _ensure_deps_installed(self) -> None:
        """
        stoke.toml의 deps에 있는 라이브러리들이 vcpkg에 설치돼있는지 확인.
        없으면 자동 설치.
        """
        if not self.target.deps:
            return

        from stoke.vcpkg import (
            is_vcpkg_installed,
            is_library_installed,
            install_library,
        )

        if not is_vcpkg_installed():
            raise RuntimeError(
                "vcpkg is not installed but target has deps.\n"
                "  Run 'stoke install vcpkg' first"
            )

        # 언어별 호환성 재검증 (사용자가 stoke.toml 직접 수정한 경우)
        if self.compiler_kind == "c":
            from stoke.c_libraries import can_use_in_c_project
            for lib_name in self.target.deps:
                if not can_use_in_c_project(lib_name):
                    raise RuntimeError(
                        f"'{lib_name}' is not a C library.\n"
                        f"  Cannot use in C project '{self.target.name}'"
                    )

        # 설치 여부 확인 + 필요 시 설치
        needs_install = []
        for lib_name, version in self.target.deps.items():
            if not is_library_installed(lib_name):
                needs_install.append((lib_name, version))

        if not needs_install:
            return

        print(f"\n--- Installing dependencies ---")
        for lib_name, version in needs_install:
            actual_version = None if version == "latest" else version
            try:
                install_library(lib_name, actual_version)
            except RuntimeError as e:
                raise RuntimeError(
                    f"Failed to install dependency '{lib_name}':\n  {e}"
                )

    def _lock_changed(self, lock, compiler: CompilerInstall) -> bool:
        """
        lock 파일의 컴파일러 정보 또는 라이브러리 정보가 현재랑 다른지 확인.
        다르면 True (저장 필요), 같으면 False (skip).
        """
        if lock is None:
            return True

        # 컴파일러 정보 비교
        current_lock = lock.c if self.compiler_kind == "c" else lock.cpp
        if current_lock is None:
            return True

        standard = self._get_standard() or ""
        if (current_lock.version != compiler.version
                or current_lock.executable != str(compiler.executable)
                or current_lock.standard != standard):
            return True

        # 라이브러리 정보 비교
        current_deps = lock.c_deps if self.compiler_kind == "c" else lock.cpp_deps
        installed_deps = self._collect_deps_for_lock()

        # 라이브러리 이름 목록 비교
        if set(current_deps.keys()) != set(installed_deps.keys()):
            return True

        # 각 라이브러리 버전/트리플렛 비교
        for name, info in installed_deps.items():
            lock_dep = current_deps[name]
            if lock_dep.version != info["version"]:
                return True
            if lock_dep.triplet != info["triplet"]:
                return True

        return False

    def _save_lock(self, compiler: CompilerInstall) -> None:
        """
        lock 파일에 현재 컴파일러 정보와 vcpkg 라이브러리 정보 저장.
        """
        standard = self._get_standard() or ""

        # vcpkg 라이브러리 정보 수집
        deps_for_lock = self._collect_deps_for_lock()

        if self.compiler_kind == "c":
            from stoke.lock import CDep
            c_deps_for_lock = {name: CDep(**info) for name, info in deps_for_lock.items()}
            lock_path, lock_changed = save_lock(
                self.project_root,
                self.project.lock_mode,
                c_compiler="gcc",
                c_version=compiler.version,
                c_executable=str(compiler.executable),
                c_standard=standard,
                c_deps=c_deps_for_lock if c_deps_for_lock else None,
            )
        else:  # cpp
            from stoke.lock import CppDep
            cpp_deps_for_lock = {name: CppDep(**info) for name, info in deps_for_lock.items()}
            lock_path, lock_changed = save_lock(
                self.project_root,
                self.project.lock_mode,
                cpp_compiler="g++",
                cpp_version=compiler.version,
                cpp_executable=str(compiler.executable),
                cpp_standard=standard,
                cpp_deps=cpp_deps_for_lock if cpp_deps_for_lock else None,
            )
        if lock_changed:
            print(f"Lock file saved: {lock_path}")

    def _collect_deps_for_lock(self) -> dict[str, dict]:
        """
        stoke.toml의 deps에 있는 라이브러리들의 실제 vcpkg 정보 수집.
        반환: {name: {"version": str, "triplet": str}}
        """
        if not self.target.deps:
            return {}

        from stoke.vcpkg import (
            is_vcpkg_installed,
            get_triplet,
            get_installed_library_version,
        )

        if not is_vcpkg_installed():
            return {}

        triplet = get_triplet()
        result = {}
        for name in self.target.deps:
            version = get_installed_library_version(name, triplet)
            if version is not None:
                result[name] = {
                    "version": version,
                    "triplet": triplet,
                }
        return result
        
    def build(self, force: bool = False) -> None:
        compiler = self.resolve_compiler()
        cache = load_cache(self.project_root)
        lock = load_lock(self.project_root, self.project.lock_mode)
        print(f"Using {self.compiler_kind} compiler {compiler.version}")
        if self.verbose:
            print(f"  executable: {compiler.executable}")

        # 의존성 확인/설치
        self._ensure_deps_installed()

        # 소스 수집
        if self.verbose:
            print("\n--- Collecting sources ---")

        source_files = self.collect_source_files()

        if not source_files:
            print("No source files found matching sources patterns")
            self._ensure_gitignore()
            return

        if self.verbose:
            print(f"Found {len(source_files)} source file(s)")

        # 컴파일
        if self.verbose:
            print("\n--- Compiling ---")

        results, skipped = self.compile_all(compiler, source_files, cache, force=force)
        failed = [r for r in results if not r.ok]
        newly_compiled = len(source_files) - len(skipped)

        if not failed:

            # 컴파일 요약: "Compiled N file(s), Skipped M"
            parts = []
            if newly_compiled > 0:
                parts.append(f"Compiled {newly_compiled} file(s)")
            if skipped:
                parts.append(f"Skipped {len(skipped)} unchanged file(s)")
            if parts:
                print(", ".join(parts))
        if failed:
            print("\nCompilation failed:")
            for result in failed:
                print(result.error)
                print()
            save_cache(self.project_root, cache)
            self._ensure_gitignore()
            raise RuntimeError(
                f"Compilation failed: {len(failed)} of {len(results)} files"
            )

        # 링크
        if self.verbose:
            print("\n--- Linking ---")        
            
        try:
            self.link(compiler, source_files)
            if self.verbose:
                print(f"Executable: {self.output_path}")
        except RuntimeError as e:
            save_cache(self.project_root, cache)
            self._ensure_gitignore()
            raise

        # 캐시 저장
        save_cache(self.project_root, cache)
        # lock 파일 저장 (변경 시에만)
        if self._lock_changed(lock, compiler):
            self._save_lock(compiler)
        # .gitignore 관리
        self._ensure_gitignore()
        # IDE 통합 파일 생성
        self._generate_ide_files(compiler, source_files)
        print(f"\nBuild complete: {self.target.name}")

    def run(self) -> int:
        """실행 파일 실행."""
        if not self.output_path.exists():
            raise RuntimeError(
                f"Executable not found: {self.output_path}\n"
                f"  Run 'stoke build' first."
            )

        print(f"Running: {self.output_path}\n")
        try:
            result = subprocess.run([str(self.output_path)])
            return result.returncode
        except KeyboardInterrupt:
            return 130

    def get_run_command(self) -> list[str]:
        """hot-reload용 실행 명령어."""
        if not self.output_path.exists():
            raise RuntimeError(
                f"Executable not found: {self.output_path}\n"
                f"  Run 'stoke build' first."
            )
        return [str(self.output_path)]