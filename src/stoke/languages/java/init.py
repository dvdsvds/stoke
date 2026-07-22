"""Java 프로젝트 초기화 로직."""
from pathlib import Path

from stoke.prompts import _prompt, _prompt_choice

def _select_java_version() -> str:
    """자바 JDK 감지 후 버전 선택."""
    from stoke.languages.java.versions import detect_all as detect_java
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

def _write_example_java(project_root: Path, project_name: str) -> tuple[Path, str]:
    """
    자바 예시 파일 생성.
    반환: (main.java 경로, main_class 문자열)
    """
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