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
    """언어 선택. 반환: 'python', 'java', 'c', 'cpp', 'go'."""
    choices = [
        "Python  (.py)",
        "Java    (.java)",
        "C       (.c)",
        "C++     (.cpp)",
        "Go      (.go)",
    ]
    languages = ["python", "java", "c", "cpp", "go"]
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
    print(f"\nCreated {stoke_toml_path}")
    print("Next: run 'stoke build' to build your project.")