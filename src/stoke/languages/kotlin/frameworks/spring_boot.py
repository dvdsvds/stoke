"""Spring Boot (Kotlin) 프로젝트 스캐폴딩."""
import sys
import subprocess
import shutil
from pathlib import Path

from stoke.prompts import _prompt, resolve_project_dir

def cmd_init_spring_boot_kotlin():
    """stoke init spring-boot-kotlin 명령어."""
    print("Creating Spring Boot (Kotlin) project\n")

    project_name, project_path, is_empty = resolve_project_dir("myapp")
    package_name = project_name.lower().replace("-", "_")

    _write_stoke_toml(project_path, project_name)
    _write_settings_gradle(project_path / "settings.gradle.kts", project_name)
    _write_build_gradle(project_path / "build.gradle.kts")

    src_dir = project_path / "src" / "main" / "kotlin" / package_name
    src_dir.mkdir(parents=True, exist_ok=True)
    _write_application_kt(src_dir / "Application.kt", package_name)

    gradle_exe = shutil.which("gradle")
    if gradle_exe:
        print("\nGenerating Gradle wrapper...")
        subprocess.run(
            [gradle_exe, "wrapper"],
            cwd=str(project_path),
            capture_output=True,
        )
    else:
        print("\nWarning: 'gradle' not found. Install Gradle from https://gradle.org/install", file=sys.stderr)

    print(f"\nSpring Boot (Kotlin) project created at: {project_path}")
    print()
    print("Next steps:")
    if not is_empty:
        print(f"  cd {project_name}")
    print(f"  stoke build")
    print(f"  stoke run")
    print()
    print("After running, open: http://localhost:8080/")

def _write_stoke_toml(project_path: Path, project_name: str) -> None:
    content = f'''[project]
name = "{project_name}"
version = "0.1.0"
lock_mode = "commit"

[targets.{project_name}]
language = "kotlin"
'''
    (project_path / "stoke.toml").write_text(content, encoding="utf-8")

def _write_settings_gradle(path: Path, project_name: str) -> None:
    content = f'rootProject.name = "{project_name}"\n'
    path.write_text(content, encoding="utf-8")

def _write_build_gradle(path: Path) -> None:
    content = '''plugins {
    id("org.springframework.boot") version "3.3.4"
    id("io.spring.dependency-management") version "1.1.6"
    kotlin("jvm") version "1.9.24"
    kotlin("plugin.spring") version "1.9.24"
}

repositories {
    mavenCentral()
}

dependencies {
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.jetbrains.kotlin:kotlin-reflect")
}
'''
    path.write_text(content, encoding="utf-8")

def _write_application_kt(path: Path, package_name: str) -> None:
    content = f'''package {package_name}

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.PathVariable
import org.springframework.web.bind.annotation.RestController

@SpringBootApplication
class Application

fun main(args: Array<String>) {{
    runApplication<Application>(*args)
}}

@RestController
class HomeController {{
    @GetMapping("/")
    fun home() = "Hello from Spring Boot (Kotlin) + stoke!"

    @GetMapping("/hello/{{name}}")
    fun hello(@PathVariable name: String) = "Hello, $name!"
}}
'''
    path.write_text(content, encoding="utf-8")
