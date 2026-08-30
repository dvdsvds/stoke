"""빌드, 실행, watch, hot-reload 명령어."""
import dataclasses
import io
import os
import re
import sys
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from stoke.adapters import make_adapter
from stoke.cli.utils import load_config_or_exit, resolve_target_or_exit, check_profile_or_exit
from stoke.hooks import run_hooks
from stoke.depgraph import closure, build_waves

# run에서 --entry-file로 override 가능한 언어. 이 어댑터들은 target.entry(스크립트 경로)로
# 실행할 스크립트를 찾음 — Java(main_class)/C/C++(컴파일된 바이너리)는 entry 개념이 없어서 제외.
_ENTRY_OVERRIDABLE_LANGUAGES = {"python", "javascript", "typescript", "ruby", "php"}

# 휴리스틱: 주석/문자열까지 파싱하지는 않음 — "int main(" / "void main(" 형태면 진입점으로 간주.
_CPP_MAIN_RE = re.compile(r"\b(?:int|void)\s+main\s*\(")

def _has_main(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    return bool(_CPP_MAIN_RE.search(text))

def _find_adhoc_cpp_entry(config, project_root, name: str):
    """
    stoke.toml에 target으로 선언 안 된 이름으로 'stoke run <이름>'이 들어왔을 때,
    C/C++ 타겟들의 sources 중 파일명(확장자 제외)이 일치하는 파일을 찾아준다.
    반환: (해당 파일이 속한 타겟, 그 타겟의 전체 소스 목록, 매칭된 파일) 또는 못 찾으면 None.
    """
    for target in config.targets.values():
        if target.language not in ("c", "cpp") or target.build_system in ("cmake", "meson"):
            continue
        adapter = make_adapter(target, config.project, project_root)
        source_files = adapter.collect_source_files()
        for f in source_files:
            if f.stem == name:
                return target, source_files, f
    return None

def _run_adhoc_cpp_entry(config, project_root, target_name: str, owner_target, source_files, entry_source, profile: str) -> None:
    """
    target으로 선언 안 된 소스 파일(예: src/sim.cpp)을 그 자리에서 빌드해서 실행.
    같은 타겟의 다른 소스 중 main()이 없는 파일들(공용 코드)은 같이 컴파일하고,
    main()이 있는 다른 파일(다른 진입점)은 빼서 다중 정의 링크 에러를 피한다.
    """
    if not _has_main(entry_source):
        rel = entry_source.relative_to(project_root)
        print(f"Error: '{rel}' has no main() function, nothing to run", file=sys.stderr)
        sys.exit(1)

    shared = [f for f in source_files if f != entry_source and not _has_main(f)]
    adhoc_sources = [entry_source] + shared
    sources_rel = [str(f.relative_to(project_root)).replace("\\", "/") for f in adhoc_sources]
    adhoc_target = dataclasses.replace(owner_target, name=target_name, sources=sources_rel)

    print(f"Ad hoc target '{target_name}': {sources_rel[0]}" + (f" (+{len(shared)} shared file(s))" if shared else ""))

    try:
        profile_obj = config.profiles[profile]
        adapter = make_adapter(adhoc_target, config.project, project_root, profile=profile_obj)
        adapter.build(force=False)
        exit_code = adapter.run()
        sys.exit(exit_code)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def _build_one(config, target_name: str, project_root, profile_obj, force: bool, verbose: bool) -> None:
    """의존성 해석 없이 타겟 하나만 빌드. 실패 시 RuntimeError 전파."""
    target = config.targets[target_name]
    if force:
        print(f"Building '{target.name}' ({target.language}) [force rebuild]...")
    else:
        print(f"Building '{target.name}' ({target.language})...")
    run_hooks(target.pre_build, project_root, "pre_build")
    adapter = make_adapter(target, config.project, project_root, profile=profile_obj, verbose=verbose)
    adapter.build(force=force)
    run_hooks(target.post_build, project_root, "post_build")

def cmd_build(target_name, force: bool = False, profile: str = "debug", verbose: bool = False):
    config = load_config_or_exit()
    check_profile_or_exit(config, profile)
    target_name = resolve_target_or_exit(config, target_name, verb="using", verbose=verbose)
    project_root = config.config_path.parent
    profile_obj = config.profiles[profile]

    # depends_on의 전이적 의존성을 먼저, 요청한 타겟을 마지막에 (의존성은 force 적용 안 함)
    build_order = closure(config.targets, target_name)

    try:
        for name in build_order:
            _build_one(config, name, project_root, profile_obj, force=(force and name == target_name), verbose=verbose)
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
    stoke build --all: stoke.toml의 모든 타겟을 빌드.
    depends_on으로 선언된 의존성은 먼저 끝나야 함 — 의존성 그래프를 파도(wave) 단위로
    나눠서, 같은 파도 안의(서로 독립적인) 타겟들만 병렬로 돌리고 다음 파도로 넘어감.
    의존성이 실패하면 그 의존성에 걸린 타겟들은 아예 시도하지 않고 스킵 처리.
    project.jobs로 파도 내 동시 실행 개수 제어(C/C++ 파일 단위 병렬 컴파일과 같은 설정 재사용).
    """
    config = load_config_or_exit()
    check_profile_or_exit(config, profile)
    project_root = config.config_path.parent
    profile_obj = config.profiles[profile]

    target_names = list(config.targets.keys())
    if not target_names:
        print("No targets defined in stoke.toml", file=sys.stderr)
        sys.exit(1)

    waves = build_waves(config.targets, target_names)
    max_workers = min(config.project.jobs or os.cpu_count() or 1, len(target_names))
    print(f"Building {len(target_names)} target(s) in {len(waves)} wave(s) (up to {max_workers} in parallel per wave)...")

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
        for wave in waves:
            # 이 파도의 타겟 중 의존성이 이미 실패한 건 시도하지 않고 스킵으로 기록
            runnable = []
            for name in wave:
                failed_dep = next((d for d in config.targets[name].depends_on if not results.get(d, (True,))[0]), None)
                if failed_dep is not None:
                    results[name] = (False, "", f"skipped: dependency '{failed_dep}' failed")
                else:
                    runnable.append(name)

            if not runnable:
                continue

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(build_one, name): name for name in runnable}
                for future in as_completed(futures):
                    name, ok, output, error = future.result()
                    results[name] = (ok, output, error)
    finally:
        # 각 with 블록이 끝나면 그 파도의 워커가 전부 join된 뒤이므로, 전체가 끝나면 딱 한 번만 복구.
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

def cmd_run(target_name, entry_file: str | None = None, profile: str = "debug"):
    config = load_config_or_exit()
    check_profile_or_exit(config, profile)
    project_root = config.config_path.parent

    # target_name이 stoke.toml에 선언된 타겟이 아니면, C/C++ 소스 파일명과 일치하는지
    # 확인 (예: src/sim.cpp가 있으면 'stoke run sim'으로 즉석 빌드/실행).
    if target_name is not None and target_name not in config.targets:
        found = _find_adhoc_cpp_entry(config, project_root, target_name)
        if found is not None:
            owner_target, source_files, entry_source = found
            _run_adhoc_cpp_entry(config, project_root, target_name, owner_target, source_files, entry_source, profile)
            return

    # run은 verbose=True로 항상 표시 (기존 동작 유지)
    target_name = resolve_target_or_exit(config, target_name, verb="running", verbose=True)
    target = config.targets[target_name]

    if entry_file is not None:
        if target.language not in _ENTRY_OVERRIDABLE_LANGUAGES:
            print(
                f"Error: '{target.language}' targets don't use an entry file "
                f"({', '.join(sorted(_ENTRY_OVERRIDABLE_LANGUAGES))} only)",
                file=sys.stderr,
            )
            sys.exit(1)
        if not (project_root / entry_file).exists():
            print(f"Error: entry file not found: {project_root / entry_file}", file=sys.stderr)
            sys.exit(1)
        target = dataclasses.replace(target, entry=entry_file)

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