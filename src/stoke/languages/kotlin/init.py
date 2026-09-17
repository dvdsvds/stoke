"""Kotlin 프로젝트 초기화 로직."""
import json
import subprocess
import shutil
import sys
import urllib.error
import urllib.request
from pathlib import Path

from stoke.languages.java.init import _select_java_version as _select_kotlin_jdk

def _current_gradle_version() -> str | None:
    """
    Gradle 공식 API로 현재 안정 버전 조회.
    Debian/Ubuntu의 apt gradle 패키지가 아주 오래된 버전(예: 4.4.1)인 경우가 흔해서,
    시스템 gradle로 그냥 `gradle wrapper`를 돌리면 그 오래된 버전 그대로 wrapper가
    찍혀 최신 JDK와 호환이 깨짐. 항상 최신 안정 버전을 명시적으로 지정해서 우회.
    네트워크 실패 시 None 반환 (호출 쪽에서 시스템 gradle 버전으로 폴백).
    """
    try:
        req = urllib.request.Request("https://services.gradle.org/versions/current")
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))["version"]
    except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError):
        return None

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
        wrapper_cmd = [gradle_exe, "wrapper"]
        gradle_version = _current_gradle_version()
        if gradle_version:
            wrapper_cmd += ["--gradle-version", gradle_version]
        result = subprocess.run(
            wrapper_cmd,
            cwd=str(project_root),
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print("Warning: gradle wrapper failed:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)

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

