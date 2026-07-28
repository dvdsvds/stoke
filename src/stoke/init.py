import sys
import tempfile
import tomllib
from pathlib import Path

from stoke.languages.python.versions import detect_all, PythonInstall
from stoke.prompts import _prompt, _prompt_choice, _prompt_yes_no
from stoke.languages.python.init import (
    _select_python_version,
    _select_env_type,
    _write_stoke_toml_python,
    _write_example_python,
)
from stoke.languages.java.init import (
    _select_java_version,
    _write_stoke_toml_java,
    _write_example_java,
)
from stoke.languages.c.init import (
    _select_c_standard,
    _prompt_vcpkg_install,
    _write_stoke_toml_c,
    _write_example_c,
)
from stoke.languages.cpp.init import (
    _select_cpp_standard,
    _write_stoke_toml_cpp,
    _write_example_cpp,
)
from stoke.languages.go.init import (
    _write_stoke_toml_go,
    _write_example_go,
    _write_example_go_subdir,
)
from stoke.languages.rust.init import (
    _select_rust_version,
    _write_rust_toolchain,
    _write_stoke_toml_rust,
    _write_example_rust,
    _write_example_rust_subdir,
    _add_rust_workspace_member,
)
from stoke.languages.kotlin.init import (
    _select_kotlin_jdk,
    _write_stoke_toml_kotlin,
    _write_example_kotlin,
    _write_example_kotlin_subdir,
    _add_gradle_module,
)
from stoke.languages.csharp.init import (
    _select_csharp_version,
    _write_global_json,
    _write_stoke_toml_csharp,
    _write_example_csharp,
    _write_example_csharp_subdir,
    _exclude_subdir_from_root_csproj,
)
from stoke.languages.ruby.init import (
    _select_ruby_version,
    _write_ruby_version_file,
    _write_stoke_toml_ruby,
    _write_example_ruby,
)
from stoke.languages.php.init import (
    _select_php_version,
    _write_composer_json_pin,
    _write_stoke_toml_php,
    _write_example_php,
)
from stoke.languages.javascript.init import (
    _write_stoke_toml_javascript,
    _write_example_javascript,
)
from stoke.languages.typescript.init import (
    _write_stoke_toml_typescript,
    _write_example_typescript,
)

def _select_lock_mode() -> str:
    """lock 파일 위치 선택."""
    choices = [
        "commit  - Lock file at project root (stoke.lock), commit to git for team reproducibility",
        "local   - Lock file inside .stoke/ (gitignored), each developer has their own",
    ]
    selected = _prompt_choice(
        "Lock file mode:",
        choices,
        default_index=0,
    )
    return "commit" if selected == 0 else "local"

def _select_language() -> str:
    choices = [
        "Python      (.py)",
        "Java        (.java)",
        "C           (.c)",
        "C++         (.cpp)",
        "Go          (.go)",
        "Rust        (.rs)",
        "Kotlin      (.kt)",
        "C#          (.cs)",
        "Ruby        (.rb)",
        "PHP         (.php)",
        "JavaScript  (.js)",
        "TypeScript  (.ts)",
    ]
    languages = ["python", "java", "c", "cpp", "go", "rust", "kotlin", "csharp", "ruby", "php", "javascript", "typescript"]
    selected = _prompt_choice(
        "Language:",
        choices,
        default_index=0,
    )
    return languages[selected]

# 타겟별로 sources/entry를 좁혀서 진짜 독립적으로 빌드되는 언어들.
# (target.sources/target.entry로 "이 타겟은 이 파일들"이라고 범위를 좁힘)
_SCOPED_LANGUAGES = ["python", "java", "c", "cpp", "ruby", "php", "javascript", "typescript"]

# Go/Rust/Kotlin은 sources/entry 필드를 안 쓰지만(어댑터가 항상 알아서 판단),
# <target_name>/ 서브디렉토리 구조로 독립적으로 빌드 가능하도록 어댑터를 고쳐둠:
#   - Go: <target_name>/에 .go 파일이 있으면 그걸 빌드 (go.mod 하나 밑에 여러
#     main 패키지를 두는 Go 표준 관례)
#   - Rust: <target_name>/에 자체 Cargo.toml이 있으면 그걸 씀 (Cargo 워크스페이스
#     멤버 -- 루트 Cargo.toml에 [workspace] members로 등록)
#   - Kotlin: <target_name>/에 자체 build.gradle.kts가 있으면 ":<target_name>:<task>"로
#     범위를 좁혀서 실행 (Gradle 멀티 프로젝트 빌드 -- 루트 settings.gradle.kts에
#     include("<target_name>")로 등록)
#   - C#: <target_name>/에 자체 .csproj가 있으면 그걸 dotnet build에 명시적으로
#     넘겨서 그 프로젝트만 빌드 (.sln 없이도 동작). 다만 루트 .csproj(첫 타겟)는
#     SDK 기본 아이템 glob이 재귀적이라 새 서브디렉토리를 자기 컴파일 대상으로
#     끌어들이므로, 루트 .csproj에 <Compile Remove="<target_name>/**" /> 제외
#     규칙을 추가해야 함 (Rust workspace members/Gradle include()에 준하는 patch)
# 그래서 _SCOPED_LANGUAGES에는 안 넣지만(경로 접두어 로직이 안 맞아서)
# _WHOLE_PROJECT_LANGUAGES에도 안 넣음(경고 대상 아님) — 각각 별도로 처리.

# 타겟이 뭐든 상관없이 항상 프로젝트 루트 전체를 그 언어 빌드 도구로 통째로 빌드하는 언어들.
# 두 번째 타겟을 추가해도 독립적으로 빌드되지 않고 같은 루트 프로젝트를
# 다시 빌드할 뿐이라 별도 경고가 필요함.
# (Go, Rust, Kotlin, C#은 전부 여기 있었는데 어댑터를 고쳐서 뺌 -- 위 주석 참조.
# 이제 비어있음 -- whole-project 문제로 남아있는 언어 없음.)
_WHOLE_PROJECT_LANGUAGES = []
_WHOLE_PROJECT_BUILD_TOOL = {}

def _read_existing_target_names(stoke_toml_path: Path) -> set[str]:
    with open(stoke_toml_path, "rb") as f:
        data = tomllib.load(f)
    return set(data.get("targets", {}).keys())

def _serialize_toml_value(value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return f'"{value}"'
    if isinstance(value, list):
        return "[" + ", ".join(_serialize_toml_value(v) for v in value) + "]"
    return str(value)

def _serialize_target_table(target_name: str, table: dict) -> str:
    """tomllib로 파싱한 타겟 딕셔너리를 [targets.<name>] TOML 텍스트로 직렬화."""
    lines = [f"[targets.{target_name}]"]
    sub_tables = {}
    for key, value in table.items():
        if isinstance(value, dict):
            sub_tables[key] = value
        else:
            lines.append(f"{key} = {_serialize_toml_value(value)}")
    text = "\n".join(lines) + "\n"
    for sub_name, sub_table in sub_tables.items():
        text += f"\n[targets.{target_name}.{sub_name}]\n"
        for k, v in sub_table.items():
            text += f"{k} = {_serialize_toml_value(v)}\n"
    return text

def _prefix_target_paths(table: dict, prefix: str) -> dict:
    """sources/entry 같은 경로 필드 앞에 '<prefix>/'를 붙임 (타겟별 하위 디렉토리 구조용)."""
    result = dict(table)
    for field in ("sources", "entry"):
        if field in result:
            value = result[field]
            if isinstance(value, list):
                result[field] = [f"{prefix}/{v}" for v in value]
            elif isinstance(value, str):
                result[field] = f"{prefix}/{value}"
    return result

def _add_target_flow(cwd: Path, stoke_toml_path: Path) -> None:
    """
    기존 stoke.toml에 새 타겟을 추가.
    Python/Java/C/C++/Ruby/PHP/JS/TS는 <타겟이름>/src/ 밑에 독립된 소스를 생성.
    Go/Rust/Kotlin/C#은 각자의 멀티 프로젝트 관례(Go 멀티 패키지, Cargo workspace,
    Gradle 멀티 프로젝트, 개별 .csproj)를 이용해 <타겟이름>/ 밑에 독립된 프로젝트를 생성.
    """
    existing_names = _read_existing_target_names(stoke_toml_path)

    while True:
        target_name = _prompt("Target name")
        if not target_name or not target_name.replace("_", "").replace("-", "").isalnum():
            print("Error: target name must be alphanumeric (- or _ allowed)", file=sys.stderr)
            continue
        if target_name in existing_names:
            print(f"Error: target '{target_name}' already exists in stoke.toml", file=sys.stderr)
            continue
        break

    language = _select_language()

    if language in _WHOLE_PROJECT_LANGUAGES:
        tool = _WHOLE_PROJECT_BUILD_TOOL[language]
        print(
            f"\nWarning: {language} always builds the entire project root regardless of "
            f"target, since its build tool ({tool}) has no concept of a per-target source "
            f"subset. A second {language} target will share the same root-level project as "
            f"any other {language} target -- it won't be independently buildable. stoke will "
            f"add the stoke.toml entry but won't generate new source files, to avoid "
            f"overwriting whatever's already at the project root."
        )
        if not _prompt_yes_no("Continue anyway?", default=False):
            print("Aborted.")
            return

    # 언어별 프롬프트 + 임시 stoke.toml에 [targets.<name>] 조각 생성
    # (기존 언어별 _write_stoke_toml_X()를 그대로 재사용 -- project_name 자리에
    # target_name을 넣어서 부르고, [project] 부분은 버리고 [targets.*]만 씀)
    tmp_dir = tempfile.mkdtemp()
    try:
        tmp_toml = Path(tmp_dir) / "stoke.toml"

        if language == "python":
            installs = detect_all()
            python_version = _select_python_version(installs)
            env_type = _select_env_type()
            _write_stoke_toml_python(tmp_toml, target_name, python_version, "commit", env_type)
        elif language == "java":
            java_version = _select_java_version()
            _write_stoke_toml_java(tmp_toml, target_name, java_version, "Main", "commit")
        elif language == "c":
            c_standard = _select_c_standard()
            _write_stoke_toml_c(tmp_toml, target_name, c_standard, "commit")
            _prompt_vcpkg_install()
        elif language == "cpp":
            cpp_standard = _select_cpp_standard()
            _write_stoke_toml_cpp(tmp_toml, target_name, cpp_standard, "commit")
            _prompt_vcpkg_install()
        elif language == "go":
            _write_stoke_toml_go(tmp_toml, target_name, "commit")
        elif language == "rust":
            _write_stoke_toml_rust(tmp_toml, target_name, "commit")
        elif language == "kotlin":
            kotlin_jdk_version = _select_kotlin_jdk()
            _write_stoke_toml_kotlin(tmp_toml, target_name, kotlin_jdk_version, "commit")
        elif language == "csharp":
            _write_stoke_toml_csharp(tmp_toml, target_name, "commit")
        elif language == "ruby":
            _write_stoke_toml_ruby(tmp_toml, target_name, "commit")
        elif language == "php":
            _write_stoke_toml_php(tmp_toml, target_name, "commit")
        elif language == "javascript":
            _write_stoke_toml_javascript(tmp_toml, target_name, "commit")
        elif language == "typescript":
            _write_stoke_toml_typescript(tmp_toml, target_name, "commit")

        with open(tmp_toml, "rb") as f:
            target_table = tomllib.load(f)["targets"][target_name]
    finally:
        import shutil
        shutil.rmtree(tmp_dir, ignore_errors=True)

    target_root = cwd / target_name

    if language in _SCOPED_LANGUAGES:
        target_table = _prefix_target_paths(target_table, target_name)

        if language == "python":
            _write_example_python(target_root)
        elif language == "java":
            _, main_class = _write_example_java(target_root, target_name)
            target_table["main_class"] = main_class
        elif language == "c":
            _write_example_c(target_root)
        elif language == "cpp":
            _write_example_cpp(target_root)
        elif language == "ruby":
            _write_example_ruby(target_root)
        elif language == "php":
            _write_example_php(target_root)
        elif language == "javascript":
            _write_example_javascript(target_root)
        elif language == "typescript":
            _write_example_typescript(target_root)
    elif language == "go":
        # sources/entry 필드가 없어서 경로 접두어는 필요 없음 -- GoAdapter가
        # <target_name>/ 서브디렉토리를 알아서 찾아 빌드함 (go.mod는 프로젝트
        # 루트에 이미 있다고 가정, 첫 Go 타겟에서 생성됐을 것).
        _write_example_go_subdir(target_root, target_name)
    elif language == "rust":
        # sources/entry 필드가 없어서 경로 접두어는 필요 없음 -- RustAdapter가
        # <target_name>/Cargo.toml이 있으면 그걸 씀 (Cargo 워크스페이스 멤버).
        # 루트 Cargo.toml에 [workspace] members로 이 타겟을 등록해야
        # cargo가 워크스페이스 멤버로 인식함.
        _write_example_rust_subdir(target_root, target_name)
        _add_rust_workspace_member(cwd / "Cargo.toml", target_name)
    elif language == "kotlin":
        # sources/entry 필드가 없어서 경로 접두어는 필요 없음 -- KotlinAdapter가
        # <target_name>/build.gradle.kts가 있으면 그걸 ":<target_name>:<task>"로
        # 범위를 좁혀서 실행함 (Gradle 멀티 프로젝트). 루트 settings.gradle.kts에
        # include("<target_name>")로 이 타겟을 등록해야 Gradle이 서브프로젝트로 인식함.
        _write_example_kotlin_subdir(target_root, target_name)
        _add_gradle_module(cwd / "settings.gradle.kts", target_name)
    elif language == "csharp":
        # sources/entry 필드가 없어서 경로 접두어는 필요 없음 -- CSharpAdapter가
        # <target_name>/*.csproj가 있으면 그걸 dotnet build에 명시적으로 넘겨서
        # 그 프로젝트만 빌드함. 다만 루트 .csproj(첫 타겟)는 SDK 기본 glob 때문에
        # 새 서브디렉토리를 자기 프로젝트에 끌어들이므로 exclude 규칙을 추가해야 함.
        _write_example_csharp_subdir(target_root, target_name)
        _exclude_subdir_from_root_csproj(cwd, target_name)

    target_block = _serialize_target_table(target_name, target_table)

    existing_content = stoke_toml_path.read_text(encoding="utf-8")
    with open(stoke_toml_path, "a", encoding="utf-8") as f:
        if existing_content and not existing_content.endswith("\n"):
            f.write("\n")
        f.write("\n" + target_block)

    print(f"\nAdded target '{target_name}' ({language}) to {stoke_toml_path}")
    if language in _SCOPED_LANGUAGES or language in ("go", "rust", "kotlin", "csharp"):
        print(f"Source files created under: {target_root}")
    else:
        print(f"No source files generated (see warning above) -- set up {language}'s project files at the root yourself.")
    print(f"Try: stoke build {target_name}")

def cmd_init() -> None:
    """대화형 프로젝트 초기화."""
    cwd = Path.cwd()
    stoke_toml_path = cwd / "stoke.toml"

    # 이미 있으면 타겟 추가할지 덮어쓸지 확인
    if stoke_toml_path.exists():
        print(f"stoke.toml already exists at {stoke_toml_path}")
        choice = _prompt_choice(
            "What would you like to do?",
            [
                "Add a new target to this project",
                "Overwrite (start over with a new stoke.toml)",
            ],
            default_index=0,
        )
        if choice == 0:
            _add_target_flow(cwd, stoke_toml_path)
            return
        # choice == 1: 덮어쓰기 -> 아래 기존 흐름 그대로 진행

    print("\n=== stoke project setup ===\n")

    # 1. 프로젝트 이름
    default_name = cwd.name
    project_name = _prompt("Project name", default=default_name)

    # 프로젝트 이름 검증
    if not project_name.replace("_", "").replace("-", "").isalnum():
        print(
            f"Error: project name '{project_name}' contains invalid characters",
            file=sys.stderr,
        )
        sys.exit(1)

    # 2. 언어 선택
    language = _select_language()

    # 3. 언어별 프롬프트
    if language == "python":
        installs = detect_all()
        python_version = _select_python_version(installs)
        env_type = _select_env_type()
        version_info = f"Python version:  {python_version}"
    elif language == "java":
        java_version = _select_java_version()
        version_info = f"Java version:    {java_version}"
    elif language == "c":
        c_standard = _select_c_standard()
        version_info = f"C standard:      {c_standard}"
        _prompt_vcpkg_install()
    elif language == "cpp":
        cpp_standard = _select_cpp_standard()
        version_info = f"C++ standard:    {cpp_standard}"
        _prompt_vcpkg_install()
    elif language == "go":
        version_info = "Language:        Go"
    elif language == "rust":
        rust_version = _select_rust_version()
        version_info = f"Toolchain pin:   {rust_version or '(none)'}"
    elif language == "kotlin":
        kotlin_jdk_version = _select_kotlin_jdk()
        version_info = f"JDK version:     {kotlin_jdk_version}"
    elif language == "csharp":
        csharp_version = _select_csharp_version()
        version_info = f"SDK pin:         {csharp_version or '(none)'}"
    elif language == "ruby":
        ruby_version = _select_ruby_version()
        version_info = f"Version pin:     {ruby_version or '(none)'}"
    elif language == "php":
        php_version = _select_php_version()
        version_info = f"Version pin:     {php_version or '(none)'}"
    elif language == "javascript":
        version_info = "Language:        JavaScript"
    elif language == "typescript":
        version_info = "Language:        TypeScript"

    # 4. lock 모드 선택
    lock_mode = _select_lock_mode()

    # 5. 최종 확인
    print("\n=== Summary ===")
    print(f"  Project name:    {project_name}")
    print(f"  Language:        {language}")
    print(f"  {version_info}")
    if language == "python":
        print(f"  Environment:     {env_type}")
    print(f"  Lock mode:       {lock_mode}")
    print(f"  Config file:     {stoke_toml_path}")

    if not _prompt_yes_no("\nCreate stoke.toml?", default=True):
        print("Aborted.")
        return

    # 6. 언어별 stoke.toml 생성 + 예시 파일 생성
    if language == "python":
        _write_stoke_toml_python(stoke_toml_path, project_name, python_version, lock_mode, env_type)
        _write_example_python(cwd)
    elif language == "java":
        _, main_class = _write_example_java(cwd, project_name)
        _write_stoke_toml_java(
            stoke_toml_path, project_name, java_version, main_class, lock_mode
        )
    elif language == "c":
        _write_stoke_toml_c(stoke_toml_path, project_name, c_standard, lock_mode)
        _write_example_c(cwd)
    elif language == "cpp":
        _write_stoke_toml_cpp(stoke_toml_path, project_name, cpp_standard, lock_mode)
        _write_example_cpp(cwd)
    elif language == "go":
        _write_stoke_toml_go(stoke_toml_path, project_name, lock_mode)
        _write_example_go(cwd, project_name)
    elif language == "rust":
        _write_stoke_toml_rust(stoke_toml_path, project_name, lock_mode)
        _write_example_rust(cwd, project_name)
        _write_rust_toolchain(cwd, rust_version)
    elif language == "kotlin":
        _write_stoke_toml_kotlin(stoke_toml_path, project_name, kotlin_jdk_version, lock_mode)
        _write_example_kotlin(cwd, project_name)
    elif language == "csharp":
        _write_stoke_toml_csharp(stoke_toml_path, project_name, lock_mode)
        _write_example_csharp(cwd, project_name)
        _write_global_json(cwd, csharp_version)
    elif language == "ruby":
        _write_stoke_toml_ruby(stoke_toml_path, project_name, lock_mode)
        _write_example_ruby(cwd)
        _write_ruby_version_file(cwd, ruby_version)
    elif language == "php":
        _write_stoke_toml_php(stoke_toml_path, project_name, lock_mode)
        _write_example_php(cwd)
        _write_composer_json_pin(cwd, project_name, php_version)
    elif language == "javascript":
        _write_stoke_toml_javascript(stoke_toml_path, project_name, lock_mode)
        _write_example_javascript(cwd)
    elif language == "typescript":
        _write_stoke_toml_typescript(stoke_toml_path, project_name, lock_mode)
        _write_example_typescript(cwd)
    print(f"\nCreated {stoke_toml_path}")
    print("Next: run 'stoke build' to build your project.")

_NONINTERACTIVE_LANGUAGES = [
    "python", "java", "c", "cpp", "go", "rust", "kotlin",
    "csharp", "ruby", "php", "javascript", "typescript",
]

def cmd_init_noninteractive(
    language: str,
    project_name: str | None = None,
    version: str | None = None,
    env_type: str | None = None,
    lock_mode: str = "commit",
    vcpkg: bool = False,
    yes: bool = False,
) -> None:
    """
    비대화형 프로젝트 초기화. CI나 팀 온보딩 스크립트에서 사용:

        stoke init --language=<lang> [--version=<v>] [--name=<name>]
                   [--env-type=venv|conda] [--lock-mode=commit|local]
                   [--vcpkg] [--yes]

    --version 의미는 언어마다 다름:
      python/java/kotlin: 버전 (없으면 시스템 기본 설치 사용)
      c/cpp: 표준 (c17/c++17 등, 없으면 기본값)
      rust/csharp/ruby/php: 선택적 toolchain pin (없으면 pin 안 함)
      go/javascript/typescript: 사용 안 함
    """
    if language not in _NONINTERACTIVE_LANGUAGES:
        print(f"Error: unsupported language '{language}'", file=sys.stderr)
        print(f"Supported: {', '.join(_NONINTERACTIVE_LANGUAGES)}", file=sys.stderr)
        sys.exit(1)

    if lock_mode not in ("commit", "local"):
        print(f"Error: invalid --lock-mode '{lock_mode}' (must be 'commit' or 'local')", file=sys.stderr)
        sys.exit(1)

    cwd = Path.cwd()
    stoke_toml_path = cwd / "stoke.toml"

    if stoke_toml_path.exists() and not yes:
        print(f"Error: stoke.toml already exists at {stoke_toml_path}", file=sys.stderr)
        print("  Pass --yes to overwrite.", file=sys.stderr)
        sys.exit(1)

    project_name = project_name or cwd.name
    if not project_name.replace("_", "").replace("-", "").isalnum():
        print(
            f"Error: project name '{project_name}' contains invalid characters",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Initializing '{language}' project '{project_name}' (non-interactive)...")

    if language == "python":
        env_type = env_type or "venv"
        if env_type not in ("venv", "conda"):
            print(f"Error: invalid --env-type '{env_type}' (must be 'venv' or 'conda')", file=sys.stderr)
            sys.exit(1)
        python_version = version or _default_python_version()
        _write_stoke_toml_python(stoke_toml_path, project_name, python_version, lock_mode, env_type)
        _write_example_python(cwd)
    elif language == "java":
        java_version = version or _default_java_version()
        _, main_class = _write_example_java(cwd, project_name)
        _write_stoke_toml_java(stoke_toml_path, project_name, java_version, main_class, lock_mode)
    elif language == "c":
        c_standard = version or "c17"
        _write_stoke_toml_c(stoke_toml_path, project_name, c_standard, lock_mode)
        _write_example_c(cwd)
        if vcpkg:
            _install_vcpkg_noninteractive()
    elif language == "cpp":
        cpp_standard = version or "c++17"
        _write_stoke_toml_cpp(stoke_toml_path, project_name, cpp_standard, lock_mode)
        _write_example_cpp(cwd)
        if vcpkg:
            _install_vcpkg_noninteractive()
    elif language == "go":
        _write_stoke_toml_go(stoke_toml_path, project_name, lock_mode)
        _write_example_go(cwd, project_name)
    elif language == "rust":
        _write_stoke_toml_rust(stoke_toml_path, project_name, lock_mode)
        _write_example_rust(cwd, project_name)
        if version:
            _write_rust_toolchain(cwd, version)
    elif language == "kotlin":
        kotlin_jdk_version = version or _default_java_version()
        _write_stoke_toml_kotlin(stoke_toml_path, project_name, kotlin_jdk_version, lock_mode)
        _write_example_kotlin(cwd, project_name)
    elif language == "csharp":
        _write_stoke_toml_csharp(stoke_toml_path, project_name, lock_mode)
        _write_example_csharp(cwd, project_name)
        if version:
            _write_global_json(cwd, version)
    elif language == "ruby":
        _write_stoke_toml_ruby(stoke_toml_path, project_name, lock_mode)
        _write_example_ruby(cwd)
        if version:
            _write_ruby_version_file(cwd, version)
    elif language == "php":
        _write_stoke_toml_php(stoke_toml_path, project_name, lock_mode)
        _write_example_php(cwd)
        if version:
            _write_composer_json_pin(cwd, project_name, version)
    elif language == "javascript":
        _write_stoke_toml_javascript(stoke_toml_path, project_name, lock_mode)
        _write_example_javascript(cwd)
    elif language == "typescript":
        _write_stoke_toml_typescript(stoke_toml_path, project_name, lock_mode)
        _write_example_typescript(cwd)

    print(f"Created {stoke_toml_path}")
    print("Next: run 'stoke build' to build your project.")

def _default_python_version() -> str:
    """감지된 파이썬 중 기본값의 'major.minor'. 감지 안 되면 하드코딩된 기본값."""
    installs = detect_all()
    if not installs:
        return "3.12"
    for install in installs:
        if install.is_default:
            parts = install.version.split(".")
            return ".".join(parts[:2])
    parts = installs[0].version.split(".")
    return ".".join(parts[:2])

def _default_java_version() -> str:
    """감지된 JDK 중 기본값의 메이저 버전. 감지 안 되면 하드코딩된 기본값."""
    from stoke.languages.java.versions import detect_all as detect_java
    installs = detect_java()
    if not installs:
        return "21"
    for install in installs:
        if install.is_default:
            return str(install.major_version)
    return str(installs[0].major_version)

def _install_vcpkg_noninteractive() -> None:
    """--vcpkg 플래그로 요청됐을 때 프롬프트 없이 설치 시도."""
    from stoke.vcpkg import is_vcpkg_installed, install_vcpkg

    if is_vcpkg_installed():
        return
    try:
        install_vcpkg()
    except RuntimeError as e:
        print(f"Warning: vcpkg installation failed: {e}", file=sys.stderr)