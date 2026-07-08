import sys
from pathlib import Path

from stoke.python_versions import detect_all, PythonInstall


def _prompt(question: str, default: str | None = None) -> str:
    """텍스트 입력 받기. 빈 입력이면 default 반환."""
    if default:
        prompt = f"{question} [{default}]: "
    else:
        prompt = f"{question}: "

    answer = input(prompt).strip()
    if not answer and default is not None:
        return default
    return answer


def _prompt_choice(question: str, choices: list[str], default_index: int = 0) -> int:
    """번호로 선택 받기. 1-indexed로 보여주고 0-indexed로 반환."""
    print(f"\n{question}")
    for i, choice in enumerate(choices, start=1):
        marker = " (default)" if (i - 1) == default_index else ""
        print(f"  {i}. {choice}{marker}")

    while True:
        answer = input(f"Select [1-{len(choices)}, default {default_index + 1}]: ").strip()
        if not answer:
            return default_index
        if not answer.isdigit():
            print(f"  Please enter a number between 1 and {len(choices)}")
            continue
        num = int(answer)
        if 1 <= num <= len(choices):
            return num - 1
        print(f"  Please enter a number between 1 and {len(choices)}")


def _prompt_yes_no(question: str, default: bool = True) -> bool:
    """예/아니오 입력."""
    default_str = "Y/n" if default else "y/N"
    while True:
        answer = input(f"{question} [{default_str}]: ").strip().lower()
        if not answer:
            return default
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("  Please answer 'y' or 'n'")


def _select_python_version(installs: list[PythonInstall]) -> str:
    """감지된 파이썬 중 하나 선택. 선택된 버전의 'major.minor' 문자열 반환."""
    if not installs:
        print("Error: No Python installations detected on this system", file=sys.stderr)
        sys.exit(1)

    # 표시용 문자열: "Python 3.14.0 (C:\...\python.exe)"
    choices = []
    default_index = 0
    for i, install in enumerate(installs):
        default_mark = " (system default)" if install.is_default else ""
        choices.append(f"Python {install.version}{default_mark}")
        if install.is_default:
            default_index = i

    selected_index = _prompt_choice(
        "Select Python version:",
        choices,
        default_index=default_index,
    )

    # major.minor만 반환 (예: "3.14")
    full_version = installs[selected_index].version
    parts = full_version.split(".")
    return ".".join(parts[:2])


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
    """언어 선택. 반환: 'python', 'java', 'c', 'cpp'."""
    choices = [
        "Python  (.py)",
        "Java    (.java)",
        "C       (.c)",
        "C++     (.cpp)",
    ]
    languages = ["python", "java", "c", "cpp"]
    selected = _prompt_choice(
        "Language:",
        choices,
        default_index=0,
    )
    return languages[selected]

def _select_java_version() -> str:
    """자바 JDK 감지 후 버전 선택."""
    from stoke.java_versions import detect_all as detect_java

    installs = detect_java()
    if not installs:
        print("No JDK detected. Please install a JDK first.")
        version = _prompt("Java version (e.g. 21)", default="21")
        return version

    print("\nDetected JDKs:")
    choices = []
    for install in installs:
        choices.append(f"Java {install.version} ({install.java_home})")

    selected = _prompt_choice(
        "JDK:",
        choices,
        default_index=0,
    )
    return str(installs[selected].major_version)


def _select_c_standard() -> str:
    """C 표준 선택."""
    choices = ["c17", "c11", "c99", "c89"]
    standards = ["c17", "c11", "c99", "c89"]
    selected = _prompt_choice(
        "C standard:",
        choices,
        default_index=0,
    )
    return standards[selected]


def _select_cpp_standard() -> str:
    """C++ 표준 선택."""
    choices = ["c++17", "c++20", "c++23", "c++14", "c++11"]
    standards = ["c++17", "c++20", "c++23", "c++14", "c++11"]
    selected = _prompt_choice(
        "C++ standard:",
        choices,
        default_index=0,
    )
    return standards[selected]

def _write_stoke_toml_python(
    path: Path,
    project_name: str,
    python_version: str,
    lock_mode: str,
) -> None:
    """파이썬 프로젝트용 stoke.toml 쓰기."""
    content = f'''[project]
name = "{project_name}"
version = "0.1.0"
lock_mode = "{lock_mode}"

[targets.{project_name}]
language = "python"
python_version = "{python_version}"
sources = ["src/**/*.py"]
entry = "src/main.py"

[targets.{project_name}.deps]
'''
    path.write_text(content, encoding="utf-8")

def _write_stoke_toml_java(
    path: Path,
    project_name: str,
    java_version: str,
    main_class: str,
    lock_mode: str,
) -> None:
    """자바 프로젝트용 stoke.toml 쓰기."""
    content = f'''[project]
name = "{project_name}"
version = "0.1.0"
lock_mode = "{lock_mode}"

[targets.{project_name}]
language = "java"
java_version = "{java_version}"
sources = ["src/**/*.java"]
main_class = "{main_class}"

[targets.{project_name}.deps]
'''
    path.write_text(content, encoding="utf-8")

def _write_stoke_toml_c(
    path: Path,
    project_name: str,
    c_standard: str,
    lock_mode: str,
) -> None:
    """C 프로젝트용 stoke.toml 쓰기."""
    content = f'''[project]
name = "{project_name}"
version = "0.1.0"
lock_mode = "{lock_mode}"

[targets.{project_name}]
language = "c"
c_standard = "{c_standard}"
sources = ["src/**/*.c"]
'''
    path.write_text(content, encoding="utf-8")

def _write_stoke_toml_cpp(
    path: Path,
    project_name: str,
    cpp_standard: str,
    lock_mode: str,
) -> None:
    """C++ 프로젝트용 stoke.toml 쓰기."""
    content = f'''[project]
name = "{project_name}"
version = "0.1.0"
lock_mode = "{lock_mode}"

[targets.{project_name}]
language = "cpp"
cpp_standard = "{cpp_standard}"
sources = ["src/**/*.cpp"]
'''
    path.write_text(content, encoding="utf-8")

def _write_example_python(project_root: Path) -> None:
    """파이썬 예시 파일 생성."""
    src_dir = project_root / "src"
    src_dir.mkdir(exist_ok=True)
    main_path = src_dir / "main.py"
    if not main_path.exists():
        main_path.write_text(
            'def main():\n'
            '    print("Hello from stoke!")\n'
            '\n'
            '\n'
            'if __name__ == "__main__":\n'
            '    main()\n',
            encoding="utf-8",
        )


def _write_example_java(project_root: Path, project_name: str) -> tuple[Path, str]:
    """
    자바 예시 파일 생성.
    반환: (main.java 경로, main_class 문자열)
    """
    # 패키지 이름은 프로젝트 이름 소문자로 (자바 관례)
    package_name = project_name.lower().replace("-", "_")
    src_dir = project_root / "src" / package_name
    src_dir.mkdir(parents=True, exist_ok=True)

    main_path = src_dir / "Main.java"
    if not main_path.exists():
        main_path.write_text(
            f'package {package_name};\n'
            '\n'
            'public class Main {\n'
            '    public static void main(String[] args) {\n'
            '        System.out.println("Hello from stoke!");\n'
            '    }\n'
            '}\n',
            encoding="utf-8",
        )

    return main_path, f"{package_name}.Main"


def _write_example_c(project_root: Path) -> None:
    """C 예시 파일 생성."""
    src_dir = project_root / "src"
    src_dir.mkdir(exist_ok=True)
    main_path = src_dir / "main.c"
    if not main_path.exists():
        main_path.write_text(
            '#include <stdio.h>\n'
            '\n'
            'int main(void) {\n'
            '    printf("Hello from stoke!\\n");\n'
            '    return 0;\n'
            '}\n',
            encoding="utf-8",
        )

def _write_example_cpp(project_root: Path) -> None:
    """C++ 예시 파일 생성."""
    src_dir = project_root / "src"
    src_dir.mkdir(exist_ok=True)
    main_path = src_dir / "main.cpp"
    if not main_path.exists():
        main_path.write_text(
            '#include <iostream>\n'
            '\n'
            'int main() {\n'
            '    std::cout << "Hello from stoke!" << std::endl;\n'
            '    return 0;\n'
            '}\n',
            encoding="utf-8",
        )
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
        version_info = f"Python version:  {python_version}"
    elif language == "java":
        java_version = _select_java_version()
        version_info = f"Java version:    {java_version}"
    elif language == "c":
        c_standard = _select_c_standard()
        version_info = f"C standard:      {c_standard}"
    elif language == "cpp":
        cpp_standard = _select_cpp_standard()
        version_info = f"C++ standard:    {cpp_standard}"

    # 4. lock 모드 선택
    lock_mode = _select_lock_mode()

    # 5. 최종 확인
    print("\n=== Summary ===")
    print(f"  Project name:    {project_name}")
    print(f"  Language:        {language}")
    print(f"  {version_info}")
    print(f"  Lock mode:       {lock_mode}")
    print(f"  Config file:     {stoke_toml_path}")

    if not _prompt_yes_no("\nCreate stoke.toml?", default=True):
        print("Aborted.")
        return

    # 6. 언어별 stoke.toml 생성 + 예시 파일 생성
    if language == "python":
        _write_stoke_toml_python(stoke_toml_path, project_name, python_version, lock_mode)
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

    print(f"\nCreated {stoke_toml_path}")
    print("Next: run 'stoke build' to build your project.")