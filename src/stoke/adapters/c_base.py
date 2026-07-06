"""
C/C++ 어댑터의 공통 베이스 클래스.
CAdapter, CppAdapter가 이걸 상속받아 컴파일러 이름, 표준 옵션만 다르게 구현.
"""

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
from stoke.c_versions import CompilerInstall, find_compiler
from stoke.config import Target, ProjectInfo


@dataclass
class CompileResult:
    ok: bool
    error: str = ""


class CBaseAdapter(BaseAdapter):
    """
    C/C++ 어댑터의 공통 로직.
    서브클래스가 다음을 구현해야 함:
      - compiler_kind: "c" 또는 "cpp"
      - source_extension: ".c" 또는 ".cpp"
      - default_standard: 컴파일러 기본 표준 (예: "c17", "c++17")
    """

    compiler_kind: str = ""       # 서브클래스에서 오버라이드
    source_extension: str = ""    # 서브클래스에서 오버라이드
    default_standard: str = ""    # 서브클래스에서 오버라이드
    standard_flag_prefix: str = "-std="  # gcc/g++ 공통

    def __init__(
        self,
        target: Target,
        project: ProjectInfo,
        project_root: Path,
    ):
        super().__init__(target, project, project_root)
        self.lang_dir = project_root / ".stoke" / self.compiler_kind / target.name
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
        """어떤 컴파일러를 쓸지 결정."""
        install = find_compiler(self.compiler_kind)
        if install is None:
            raise RuntimeError(
                f"No {self.compiler_kind} compiler detected.\n"
                f"  Install gcc/g++ or ensure it's in your PATH."
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
                        skipped.append(file)
                        continue

            files_to_compile.append(file)

        results = []
        if not files_to_compile:
            for _ in files:
                results.append(CompileResult(ok=True))
            return results, skipped

        # 각 파일 개별 컴파일 (병렬화는 나중에)
        for file in files_to_compile:
            obj_path = self._object_path(file)
            obj_path.parent.mkdir(parents=True, exist_ok=True)

            cmd = [str(compiler.executable)]

            # 표준 옵션
            standard = self._get_standard()
            if standard:
                cmd.append(f"{self.standard_flag_prefix}{standard}")

            # Include 경로
            for include_dir in self._include_dirs():
                cmd.extend(["-I", str(include_dir)])

            # 컴파일만 (링크 X)
            cmd.extend(["-c", str(file), "-o", str(obj_path)])

            proc = subprocess.run(cmd, capture_output=True, text=True)

            if proc.returncode == 0:
                file_key = str(file.relative_to(self.project_root))
                target_cache.syntax_check[file_key] = get_file_stat(file)
                results.append(CompileResult(ok=True))
            else:
                error_msg = proc.stderr.strip() or proc.stdout.strip()
                file_key = str(file.relative_to(self.project_root))
                target_cache.syntax_check.pop(file_key, None)
                results.append(CompileResult(ok=False, error=error_msg))

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

        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        proc = subprocess.run(cmd, capture_output=True, text=True)

        if proc.returncode != 0:
            error_msg = proc.stderr.strip() or proc.stdout.strip()
            raise RuntimeError(f"Link failed:\n{error_msg}")

    def build(self, force: bool = False) -> None:
        compiler = self.resolve_compiler()
        cache = load_cache(self.project_root)

        print(f"Using {self.compiler_kind} compiler {compiler.version}")
        print(f"  executable: {compiler.executable}")

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
        results, skipped = self.compile_all(compiler, source_files, cache, force=force)
        failed = [r for r in results if not r.ok]

        if skipped:
            print(f"  Skipped {len(skipped)} unchanged file(s)")

        newly_compiled = len(source_files) - len(skipped)
        if newly_compiled > 0 and not failed:
            print(f"  Compiled {newly_compiled} file(s)")

        if failed:
            print("\nCompilation failed:")
            print(failed[0].error)
            save_cache(self.project_root, cache)
            self._ensure_gitignore()
            raise RuntimeError(
                f"Compilation failed: {len(failed)} of {len(results)} files"
            )

        # 링크
        print("\n--- Linking ---")
        try:
            self.link(compiler, source_files)
            print(f"  Executable: {self.output_path}")
        except RuntimeError as e:
            save_cache(self.project_root, cache)
            self._ensure_gitignore()
            raise

        # 캐시 저장
        save_cache(self.project_root, cache)

        # .gitignore 관리
        self._ensure_gitignore()

        print(f"\nBuild complete: {self.target.name}")

    def run(self) -> int:
        """실행 파일 실행."""
        if not self.output_path.exists():
            raise RuntimeError(
                f"Executable not found: {self.output_path}\n"
                f"  Run 'stoke build' first."
            )

        print(f"Running: {self.output_path}\n")
        result = subprocess.run([str(self.output_path)])
        return result.returncode

    def get_run_command(self) -> list[str]:
        """hot-reload용 실행 명령어."""
        if not self.output_path.exists():
            raise RuntimeError(
                f"Executable not found: {self.output_path}\n"
                f"  Run 'stoke build' first."
            )
        return [str(self.output_path)]