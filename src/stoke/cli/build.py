"""빌드, 실행, watch, hot-reload 명령어."""
import io
import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from stoke.adapters import make_adapter
from stoke.cli.utils import load_config_or_exit, resolve_target_or_exit, check_profile_or_exit
from stoke.hooks import run_hooks

def cmd_build(target_name, force: bool = False, profile: str = "debug", verbose: bool = False):
    config = load_config_or_exit()
    check_profile_or_exit(config, profile)
    target_name = resolve_target_or_exit(config, target_name, verb="using", verbose=verbose)
    target = config.targets[target_name]
    if force:
        print(f"Building '{target.name}' ({target.language}) [force rebuild]...")
    else:
        print(f"Building '{target.name}' ({target.language})...")

    project_root = config.config_path.parent
    try:
        profile_obj = config.profiles[profile]
        run_hooks(target.pre_build, project_root, "pre_build")
        adapter = make_adapter(target, config.project, project_root, profile=profile_obj, verbose=verbose)
        adapter.build(force=force)
        run_hooks(target.post_build, project_root, "post_build")
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

class _ThreadLocalStdout:
    """
    병렬 빌드 중 각 어댑터의 print() 출력을 스레드별로 분리해서 모으는 stdout 대역.
    여러 타겟을 동시에 빌드하면 각 어댑터가 제멋대로 print()를 호출하는데,
    그대로 두면 터미널에 여러 타겟 출력이 뒤섞여서 못 읽음. sys.stdout 자체는
    프로세스 전역이라 스레드마다 따로 바꿔치기할 수 없으니, 대신 이 객체 하나를
    전역으로 꽂아두고 내부적으로 threading.local()로 스레드별 버퍼에 나눠 담음
    (실제 화면 출력은 각 타겟 빌드가 끝난 뒤 한 덩어리로 몰아서 함).
    """
    def __init__(self):
        self._local = threading.local()

    def _buffer(self) -> io.StringIO:
        if not hasattr(self._local, "buf"):
            self._local.buf = io.StringIO()
        return self._local.buf

    def write(self, text: str) -> None:
        self._buffer().write(text)

    def flush(self) -> None:
        pass

    def pop(self) -> str:
        """지금까지 이 스레드가 쓴 내용을 반환하고 버퍼 비움."""
        value = self._buffer().getvalue()
        self._local.buf = io.StringIO()
        return value

def cmd_build_all(force: bool = False, profile: str = "debug", verbose: bool = False):
    """
    stoke build --all: stoke.toml의 모든 타겟을 병렬로 빌드.
    타겟 간 의존성 개념이 없으므로(stoke.toml에 선언할 방법 자체가 없음) 전부
    서로 독립적이라고 가정하고 동시에 돌림. project.jobs로 동시 실행 개수 제어
    (C/C++가 파일 단위 병렬 컴파일에 쓰는 것과 같은 설정 재사용).
    """
    config = load_config_or_exit()
    check_profile_or_exit(config, profile)
    project_root = config.config_path.parent
    profile_obj = config.profiles[profile]

    target_names = list(config.targets.keys())
    if not target_names:
        print("No targets defined in stoke.toml", file=sys.stderr)
        sys.exit(1)

    max_workers = min(config.project.jobs or os.cpu_count() or 1, len(target_names))
    print(f"Building {len(target_names)} target(s) (up to {max_workers} in parallel)...")

    thread_stdout = _ThreadLocalStdout()

    def build_one(name: str) -> tuple[str, bool, str, str | None]:
        # 주의: 여기서 sys.stdout을 손대면 안 됨 — sys.stdout은 프로세스 전역이라,
        # 스레드마다 개별적으로 스왑/복구하면 먼저 끝난 스레드가 아직 실행 중인
        # 다른 스레드 몫까지 되돌려버리는 race가 생김 (실제로 이 버그로 출력이
        # 뒤섞이는 걸 테스트에서 확인함). 대신 병렬 구간 전체를 감싸는 쪽에서
        # 딱 한 번만 스왑/복구하고, 여기서는 thread_stdout이 이미 sys.stdout으로
        # 꽂혀있다고 가정하고 그냥 씀 — 실제 분리는 thread_stdout 내부의
        # threading.local()이 알아서 함.
        target = config.targets[name]
        try:
            run_hooks(target.pre_build, project_root, "pre_build")
            adapter = make_adapter(target, config.project, project_root, profile=profile_obj, verbose=verbose)
            adapter.build(force=force)
            run_hooks(target.post_build, project_root, "post_build")
            return name, True, thread_stdout.pop(), None
        except RuntimeError as e:
            return name, False, thread_stdout.pop(), str(e)
        except Exception as e:
            # 타겟 하나에서 예상 못한 에러가 나도 나머지 결과는 정상적으로 모아서 보고
            return name, False, thread_stdout.pop(), f"Unexpected error: {e}"

    results: dict[str, tuple[bool, str, str | None]] = {}
    real_stdout = sys.stdout
    sys.stdout = thread_stdout
    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(build_one, name): name for name in target_names}
            for future in as_completed(futures):
                name, ok, output, error = future.result()
                results[name] = (ok, output, error)
    finally:
        # with 블록이 끝나면 ThreadPoolExecutor가 모든 워커를 join한 뒤라
        # (기본 shutdown(wait=True)) 이 시점엔 전부 끝난 게 보장됨 — 딱 한 번만 복구.
        sys.stdout = real_stdout

    # 원래 타겟 순서대로 출력 (완료 순서가 아니라 stoke.toml에 적힌 순서 —
    # 병렬로 끝나는 순서는 실행마다 달라져서 재현 가능한 로그를 위해 고정 순서로 표시)
    for name in target_names:
        ok, output, error = results[name]
        status = "OK" if ok else "FAILED"
        print(f"\n=== {name} [{status}] ===")
        if output:
            print(output, end="" if output.endswith("\n") else "\n")
        if not ok:
            print(f"Error: {error}", file=sys.stderr)

    failed = [name for name in target_names if not results[name][0]]
    if failed:
        print(f"\n{len(failed)} of {len(target_names)} target(s) failed: {', '.join(failed)}", file=sys.stderr)
        sys.exit(1)

    print(f"\nBuilt {len(target_names)} target(s) successfully.")

def cmd_run(target_name, profile: str = "debug"):
    config = load_config_or_exit()
    check_profile_or_exit(config, profile)
    # run은 verbose=True로 항상 표시 (기존 동작 유지)
    target_name = resolve_target_or_exit(config, target_name, verb="running", verbose=True)
    target = config.targets[target_name]
    project_root = config.config_path.parent

    try:
        profile_obj = config.profiles[profile]
        adapter = make_adapter(target, config.project, project_root, profile=profile_obj)
        exit_code = adapter.run()
        sys.exit(exit_code)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def cmd_watch(target_name, profile: str = "debug", verbose: bool = False):
    config = load_config_or_exit()
    check_profile_or_exit(config, profile)
    target_name = resolve_target_or_exit(config, target_name, verb="watching", verbose=verbose)
    target = config.targets[target_name]
    project_root = config.config_path.parent
    profile_obj = config.profiles[profile]

    from stoke.watcher import watch

    try:
        watch(target, config, project_root, profile=profile_obj, verbose=verbose)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def cmd_hot_reload(target_name, profile: str = "debug", verbose: bool = False):
    config = load_config_or_exit()
    check_profile_or_exit(config, profile)
    target_name = resolve_target_or_exit(config, target_name, verb="hot-reloading", verbose=verbose)
    target = config.targets[target_name]

    project_root = config.config_path.parent
    profile_obj = config.profiles[profile]

    from stoke.hot_reload import hot_reload

    try:
        hot_reload(target, config, project_root, profile=profile_obj, verbose=verbose)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)