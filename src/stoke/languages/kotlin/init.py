"""Kotlin 프로젝트 초기화 로직."""
import subprocess
import shutil
from pathlib import Path

from stoke.languages.java.init import _select_java_version as _select_kotlin_jdk

def _write_stoke_toml_kotlin(
    path: Path,
    project_name: str,
    java_version: str,
    lock_mode: str,
) -> None:
    """Kotlin 프로젝트용 stoke.toml 쓰기."""
    content = f'''[project]
name = "{project_name}"
version = "0.1.0"
lock_mode = "{lock_mode}"

[targets.{project_name}]
language = "kotlin"
java_version = "{java_version}"
'''
    path.write_text(content, encoding="utf-8")

def _write_example_kotlin(project_root: Path, project_name: str) -> None:
    """Kotlin 예시 파일 생성 + Gradle Wrapper 초기화."""
    _write_settings_gradle(project_root / "settings.gradle.kts", project_name)
    _write_build_gradle(project_root / "build.gradle.kts")

    src_dir = project_root / "src" / "main" / "kotlin"
    src_dir.mkdir(parents=True, exist_ok=True)
    main_kt = src_dir / "Main.kt"
    main_kt.write_text(
        'fun main() {\n'
        '    println("Hello from stoke!")\n'
        '}\n',
        encoding="utf-8",
    )

    gradle_exe = shutil.which("gradle")
    if gradle_exe:
        subprocess.run(
            [gradle_exe, "wrapper"],
            cwd=str(project_root),
            capture_output=True,
        )

def _write_settings_gradle(path: Path, project_name: str) -> None:
    content = f'rootProject.name = "{project_name}"\n'
    path.write_text(content, encoding="utf-8")

def _write_build_gradle(path: Path) -> None:
    content = '''plugins {
    kotlin("jvm") version "1.9.24"
    application
}

repositories {
    mavenCentral()
}

application {
    mainClass.set("MainKt")
}
'''
    path.write_text(content, encoding="utf-8")

def _write_example_kotlin_subdir(target_root: Path, target_name: str) -> None:
    """
    멀티 타겟 프로젝트에 두 번째 이후 Kotlin 타겟 추가할 때 사용.
    target_root 안에 자체 build.gradle.kts + src/main/kotlin/Main.kt를 갖춘
    완전한 Gradle 서브프로젝트를 생성함. 루트 settings.gradle.kts에 이
    서브프로젝트를 등록하는 건 _add_gradle_module()이 별도로 처리.
    """
    target_root.mkdir(parents=True, exist_ok=True)
    _write_build_gradle(target_root / "build.gradle.kts")

    src_dir = target_root / "src" / "main" / "kotlin"
    src_dir.mkdir(parents=True, exist_ok=True)
    main_kt = src_dir / "Main.kt"
    main_kt.write_text(
        'fun main() {\n'
        f'    println("Hello from stoke! ({target_name})")\n'
        '}\n',
        encoding="utf-8",
    )

def _add_gradle_module(settings_gradle_path: Path, module_name: str) -> None:
    """
    루트 settings.gradle.kts에 Gradle 서브프로젝트 등록.
    이미 include("<module_name>")가 있으면 아무 것도 안 함.
    """
    if not settings_gradle_path.is_file():
        raise RuntimeError(
            f"{settings_gradle_path} not found -- expected an existing Kotlin project"
        )

    include_line = f'include("{module_name}")'
    text = settings_gradle_path.read_text(encoding="utf-8")
    if include_line in text:
        return
    if not text.endswith("\n"):
        text += "\n"
    text += f"{include_line}\n"
    settings_gradle_path.write_text(text, encoding="utf-8")

def _remove_gradle_module(settings_gradle_path: Path, module_name: str) -> None:
    """루트 settings.gradle.kts에서 include("<module_name>") 줄 제거. _add_gradle_module()의 반대."""
    if not settings_gradle_path.is_file():
        return

    include_line = f'include("{module_name}")'
    text = settings_gradle_path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    lines = [line for line in lines if line.strip() != include_line]
    settings_gradle_path.write_text("".join(lines), encoding="utf-8")
