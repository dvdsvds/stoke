import sys
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
)
from stoke.languages.rust.init import (
    _select_rust_version,
    _write_rust_toolchain,
    _write_stoke_toml_rust,
    _write_example_rust,
)
from stoke.languages.kotlin.init import (
    _select_kotlin_jdk,
    _write_stoke_toml_kotlin,
    _write_example_kotlin,
)
from stoke.languages.csharp.init import (
    _select_csharp_version,
    _write_global_json,
    _write_stoke_toml_csharp,
    _write_example_csharp,
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

def cmd_init() -> None:
    """대화형 프로젝트 초기화."""
    cwd = Path.cwd()
    stoke_toml_path = cwd / "stoke.toml"

    # 이미 있으면 덮어쓸지 확인
    if stoke_toml_path.exists():
        print(f"stoke.toml already exists at {stoke_toml_path}")
        if not _prompt_yes_no("Overwrite?", default=False):
            print("Aborted.")
            return

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