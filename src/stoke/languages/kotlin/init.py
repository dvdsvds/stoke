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
