import signal
import subprocess
import sys
import time
import threading
from pathlib import Path

from watchdog.observers import Observer

from stoke.adapters.python import PythonAdapter
from stoke.config import Config, Target
from stoke.watcher import _DebouncedHandler, _watch_roots_from_target


GRACEFUL_TIMEOUT_SECONDS = 5


class ProcessManager:
    """
    entry 파일을 서브프로세스로 실행하고 재시작을 관리.
    """

    def __init__(self, venv_python: Path, entry: Path, project_root: Path):
        self.venv_python = venv_python
        self.entry = entry
        self.project_root = project_root
        self._process: subprocess.Popen | None = None
        self._lock = threading.Lock()

    def start(self):
        """새 프로세스 시작. 이미 실행 중이면 아무 것도 안 함."""
        with self._lock:
            if self._process is not None and self._process.poll() is None:
                return

            print(f"[hot-reload] Starting: {self.entry}")
            try:
                self._process = subprocess.Popen(
                    [str(self.venv_python), str(self.entry)],
                    cwd=str(self.project_root),
                )
            except OSError as e:
                print(f"[hot-reload] Failed to start process: {e}", file=sys.stderr)
                self._process = None

    def stop(self):
        """
        graceful 종료: SIGTERM → 5초 대기 → SIGKILL.
        이미 종료된 프로세스는 즉시 반환.
        """
        with self._lock:
            if self._process is None:
                return

            # 이미 종료됨
            if self._process.poll() is not None:
                self._process = None
                return

            print(f"[hot-reload] Stopping process (pid={self._process.pid})...")

            # SIGTERM 시도
            try:
                self._process.terminate()
            except OSError:
                # 이미 죽었을 수 있음
                self._process = None
                return

            # 최대 GRACEFUL_TIMEOUT_SECONDS 대기
            try:
                self._process.wait(timeout=GRACEFUL_TIMEOUT_SECONDS)
                self._process = None
                return
            except subprocess.TimeoutExpired:
                pass

            # 여전히 살아있으면 SIGKILL
            print(f"[hot-reload] Process did not exit in {GRACEFUL_TIMEOUT_SECONDS}s, killing...")
            try:
                self._process.kill()
                self._process.wait(timeout=2)
            except OSError:
                pass
            self._process = None

    def restart(self):
        """정지 후 시작."""
        self.stop()
        self.start()


def _run_build(target: Target, config: Config, project_root: Path) -> bool:
    """빌드 실행. 성공 여부 반환. 예외는 여기서 삼킴."""
    print("\n" + "=" * 50)
    print(f"[hot-reload] Rebuilding '{target.name}'...")
    print("=" * 50)
    try:
        adapter = PythonAdapter(target, config.project, project_root)
        adapter.build()
        return True
    except RuntimeError as e:
        print(f"\n[hot-reload] Build failed: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"\n[hot-reload] Unexpected error: {e}", file=sys.stderr)
        return False


def hot_reload(target: Target, config: Config, project_root: Path):
    """hot-reload 진입점."""
    if target.language != "python":
        raise RuntimeError(
            f"Hot-reload currently only supports Python targets, "
            f"got '{target.language}'"
        )

    if not target.entry:
        raise RuntimeError(
            f"Target '{target.name}' has no 'entry' field in stoke.toml.\n"
            f"  Hot-reload needs an entry file to execute.\n"
            f"  Add 'entry = \"path/to/main.py\"' under [targets.{target.name}]"
        )

    entry_path = project_root / target.entry
    if not entry_path.exists():
        raise RuntimeError(
            f"Entry file not found: {entry_path}\n"
            f"  Check the 'entry' field in stoke.toml"
        )

    # 감시 루트 결정
    roots = _watch_roots_from_target(project_root, target)
    if not roots:
        raise RuntimeError(
            f"No watchable directories found for target '{target.name}'. "
            f"Check the 'sources' patterns in stoke.toml."
        )

    # 첫 빌드
    build_ok = _run_build(target, config, project_root)

    # venv 파이썬 경로 (빌드 성공 후에만 정확히 알 수 있음)
    adapter = PythonAdapter(target, config.project, project_root)
    venv_python = adapter.venv_python_exe()

    # 프로세스 매니저 초기화
    manager = ProcessManager(venv_python, entry_path, project_root)

    # 첫 빌드 성공하면 프로세스 시작
    if build_ok:
        manager.start()
    else:
        print("[hot-reload] Skipping process start due to build failure.")

    # 파일 변경 콜백
    def on_change(paths: set[str]):
        rel_paths = []
        for p in paths:
            try:
                rel = Path(p).relative_to(project_root)
                rel_paths.append(str(rel))
            except ValueError:
                rel_paths.append(p)
        print(f"\n[hot-reload] Detected changes in: {', '.join(sorted(rel_paths))}")

        # 재빌드
        build_ok = _run_build(target, config, project_root)

        # 재시작
        if build_ok:
            manager.restart()
        else:
            manager.stop()  # 실패 시 기존 프로세스는 죽여둠
            print("[hot-reload] Waiting for fixes...")

    # 옵저버 설정
    handler = _DebouncedHandler(on_change, {".py"})
    observer = Observer()
    for root in roots:
        observer.schedule(handler, str(root), recursive=True)
        print(f"[hot-reload] Watching: {root}")

    print("[hot-reload] Press Ctrl+C to stop.\n")
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[hot-reload] Stopping...")
        observer.stop()
        manager.stop()
    observer.join()
    print("[hot-reload] Stopped.")