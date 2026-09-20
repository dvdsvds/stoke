"""빌드, 실행, watch, hot-reload 명령어."""
import dataclasses
import re
import shutil
import subprocess
import sys
from pathlib import Path
from stoke.adapters import make_adapter
from stoke.cli.utils import load_config_or_exit, resolve_target_or_exit, check_profile_or_exit
from stoke.hooks import run_hooks

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
    """target으로 선언 안 된 이름으로 'stoke run'이 들어왔을 때 C/C++ sources에서 파일명 매칭."""
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
    """target 미선언 소스 파일을 그 자리에서 빌드/실행 (다른 main() 파일은 링크에서 제외)."""
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

def _find_adhoc_go_entry(project_root: Path, path_str: str) -> Path | None:
    """target으로 선언 안 된 값이 실제 .go 파일 경로면 반환. C/C++와 달리 파일 내용은 안 보고
    그대로 'go run <부모 디렉토리>'에 넘김 -- main() 유무/중복 검사는 go 컴파일러가 알아서 함."""
    candidate = project_root / path_str
    if candidate.is_file() and candidate.suffix == ".go":
        return candidate
    return None

def _run_adhoc_go_entry(project_root: Path, entry_file: Path) -> None:
    """go run <entry_file의 부모 디렉토리>를 그 자리에서 실행. stoke.toml에 Go 타겟 선언 여부와 무관."""
    from stoke.tool_install import toolchain_env

    env = toolchain_env("go", project_root)
    go_exe = shutil.which("go", path=env.get("PATH")) or shutil.which("go")
    if go_exe is None:
        print(
            "Error: go not found.\n  Install with: stoke install --language=go --version=latest",
            file=sys.stderr,
        )
        sys.exit(1)

    package_dir = entry_file.parent
    rel = package_dir.relative_to(project_root)
    package_path = f"./{rel}".replace("\\", "/") if str(rel) != "." else "."

    print(f"Ad hoc: go run {package_path}", flush=True)
    try:
        result = subprocess.run([go_exe, "run", package_path], cwd=str(project_root), env=env)
    except KeyboardInterrupt:
        sys.exit(130)
    sys.exit(result.returncode)

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

    try:
        _build_one(config, target_name, project_root, profile_obj, force=force, verbose=verbose)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

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

        # 또는 실제 존재하는 .go 파일 경로면 (예: 'stoke run cmd/colorpicker-preview/main.go')
        # 그 패키지 디렉토리를 그대로 go run에 위임 -- Go 타겟 선언 여부와 무관하게 동작.
        go_entry = _find_adhoc_go_entry(project_root, target_name)
        if go_entry is not None:
            _run_adhoc_go_entry(project_root, go_entry)
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

def cmd_test(target_name, profile: str = "debug", verbose: bool = False):
    config = load_config_or_exit()
    check_profile_or_exit(config, profile)
    target_name = resolve_target_or_exit(config, target_name, verb="testing", verbose=verbose)
    target = config.targets[target_name]
    project_root = config.config_path.parent
    profile_obj = config.profiles[profile]

    try:
        adapter = make_adapter(target, config.project, project_root, profile=profile_obj, verbose=verbose)
        exit_code = adapter.test(verbose=verbose)
        sys.exit(exit_code)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)