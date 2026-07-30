"""Ktor (Kotlin) 프로젝트 스캐폴딩."""
import sys
import subprocess
import shutil
from pathlib import Path

from stoke.prompts import _prompt, resolve_project_dir

def cmd_init_ktor():
    """stoke init ktor 명령어."""
    print("Creating Ktor (Kotlin) project\n")

    project_name, project_path, is_empty = resolve_project_dir("myapp")

    _write_stoke_toml(project_path, project_name)
    _write_settings_gradle(project_path / "settings.gradle.kts", project_name)
    _write_build_gradle(project_path / "build.gradle.kts")

    src_dir = project_path / "src" / "main" / "kotlin"
    src_dir.mkdir(parents=True, exist_ok=True)
    _write_main_kt(src_dir / "Main.kt")

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

    print(f"\nKtor project created at: {project_path}")
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
    kotlin("jvm") version "1.9.24"
    application
}

repositories {
    mavenCentral()
}

dependencies {
    implementation("io.ktor:ktor-server-core-jvm:2.3.12")
    implementation("io.ktor:ktor-server-netty-jvm:2.3.12")
}

application {
    mainClass.set("MainKt")
}
'''
    path.write_text(content, encoding="utf-8")

def _write_main_kt(path: Path) -> None:
    content = '''import io.ktor.server.application.*
import io.ktor.server.engine.*
import io.ktor.server.netty.*
import io.ktor.server.response.*
import io.ktor.server.routing.*

fun main() {
    embeddedServer(Netty, port = 8080) {
        routing {
            get("/") {
                call.respondText("Hello from Ktor + stoke!")
            }
            get("/hello/{name}") {
                val name = call.parameters["name"]
                call.respondText("Hello, $name!")
            }
        }
    }.start(wait = true)
}
'''
    path.write_text(content, encoding="utf-8")
