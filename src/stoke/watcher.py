import sys
import time
import threading
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from stoke.adapters import make_adapter
from stoke.config import Config, Target

DEBOUNCE_SECONDS = 0.3
# 언어별 소스 파일 확장자
LANGUAGE_EXTENSIONS = {
    "python": {".py"},
    "java": {".java"},
    "c": {".c", ".h"},
    "cpp": {".cpp", ".hpp", ".cc", ".hh"},
}

class _DebouncedHandler(FileSystemEventHandler):
    """
    파일 변경 이벤트를 받아서 디바운싱 후 콜백 실행.

    편집기가 저장 시 여러 이벤트를 순간적으로 발생시키는 걸 방지하려고,
    마지막 이벤트 후 DEBOUNCE_SECONDS 동안 조용해야 콜백이 호출됨.
    """

    def __init__(self, callback, source_extensions: set[str]):
        super().__init__()
        self._callback = callback
        self._source_extensions = source_extensions
        self._timer: threading.Timer | None = None
        self._lock = threading.Lock()
        self._pending_paths: set[str] = set()

    def _should_react(self, path: str) -> bool:
        """이 경로 변경에 반응할지 결정. .py 등 소스 확장자만."""
        p = Path(path)
        if p.suffix not in self._source_extensions:
            return False
        # __pycache__, .stoke 안의 파일은 무시
        parts = p.parts
        if "__pycache__" in parts or ".stoke" in parts:
            return False
        return True

    def _dispatch(self, event_path: str):
        if not self._should_react(event_path):
            return

        with self._lock:
            self._pending_paths.add(event_path)
            if self._timer is not None:
                self._timer.cancel()
            self._timer = threading.Timer(DEBOUNCE_SECONDS, self._fire)
            self._timer.daemon = True
            self._timer.start()

    def _fire(self):
        with self._lock:
            paths = self._pending_paths.copy()
            self._pending_paths.clear()
            self._timer = None
        if paths:
            self._callback(paths)
    
    def on_modified(self, event):
        if event.is_directory:
            return
        self._dispatch(event.src_path)

    def on_created(self, event):
        if event.is_directory:
            return
        self._dispatch(event.src_path)

    def on_deleted(self, event):
        if event.is_directory:
            return
        self._dispatch(event.src_path)

    def on_moved(self, event):
        if event.is_directory:
            return
        # 이동은 새 경로 기준으로
        self._dispatch(event.dest_path)


def _watch_roots_from_target(project_root: Path, target: Target) -> list[Path]:
    """
    sources 패턴에서 감시할 최상위 디렉토리들 추출.
    예: ["src/**/*.py"] -> [project_root/src]
    예: ["src/*.py", "tests/*.py"] -> [project_root/src, project_root/tests]
    """
    roots = set()
    for pattern in target.sources:
        # 패턴의 첫 부분(와일드카드 나오기 전)까지가 감시 루트
        parts = Path(pattern).parts
        root_parts = []
        for part in parts:
            if any(ch in part for ch in ("*", "?", "[")):
                break
            root_parts.append(part)

        if not root_parts:
            # 패턴이 처음부터 와일드카드면 project_root 자체를 감시
            roots.add(project_root)
        else:
            root = project_root / Path(*root_parts)
            # 파일 경로가 나오면 부모 폴더로
            if root.is_file():
                root = root.parent
            roots.add(root)

    # 존재하는 루트만
    return [r for r in roots if r.exists()]

def _run_build(target: Target, config: Config, project_root: Path, profile=None, verbose: bool = False):
    """한 번 빌드. 실패해도 예외를 여기서 삼켜서 watch 루프 유지."""
    print("\n" + "=" * 50)
    print(f"[watch] Rebuilding '{target.name}'...")
    print("=" * 50)
    try:
        adapter = make_adapter(target, config.project, project_root, profile=profile, verbose=verbose)
        adapter.build()
    except RuntimeError as e:
        print(f"\n[watch] Build failed: {e}", file=sys.stderr)
        print("[watch] Continuing to watch for changes...")
    except Exception as e:
        print(f"\n[watch] Unexpected error: {e}", file=sys.stderr)
        print("[watch] Continuing to watch for changes...")

def watch(target: Target, config: Config, project_root: Path, profile=None, verbose: bool = False):
    """watch 모드 진입점."""
    # 감시 루트 결정
    roots = _watch_roots_from_target(project_root, target)
    if not roots:
        raise RuntimeError(
            f"No watchable directories found for target '{target.name}'. "
            f"Check the 'sources' patterns in stoke.toml."
        )
    # 언어별 소스 확장자 결정
    source_extensions = LANGUAGE_EXTENSIONS.get(target.language)
    if not source_extensions:
        raise RuntimeError(
            f"Watch mode not supported for language '{target.language}'.\n"
            f"  Supported: {', '.join(sorted(LANGUAGE_EXTENSIONS.keys()))}"
        )
    # 첫 빌드
    _run_build(target, config, project_root, profile=profile, verbose=verbose)
    # 파일 변경 콜백
    def on_change(paths: set[str]):
        # 변경된 파일 목록 요약 출력
        rel_paths = []
        for p in paths:
            try:
                rel = Path(p).relative_to(project_root)
                rel_paths.append(str(rel))
            except ValueError:
                rel_paths.append(p)
        print(f"\n[watch] Detected changes in: {', '.join(sorted(rel_paths))}")
        _run_build(target, config, project_root, profile=profile, verbose=verbose)

    # 옵저버 설정
    handler = _DebouncedHandler(on_change, source_extensions)
    observer = Observer()
    for root in roots:
        observer.schedule(handler, str(root), recursive=True)
        print(f"[watch] Watching: {root}")

    print("[watch] Press Ctrl+C to stop.\n")
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[watch] Stopping...")
        observer.stop()
    observer.join()
    print("[watch] Stopped.")