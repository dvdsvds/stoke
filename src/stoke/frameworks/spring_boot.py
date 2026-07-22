"""Spring Boot 프로젝트 스캐폴딩 (Spring Initializr API 사용)."""
import sys
import io
import zipfile
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path

SPRING_INITIALIZR_URL = "https://start.spring.io/starter.zip"
SPRING_METADATA_URL = "https://start.spring.io/metadata/client"

def _fetch_boot_versions() -> list[str]:
    """
    Spring Initializr에서 사용 가능한 Spring Boot 버전 목록 조회.
    RELEASE 버전만 필터링.
    """
    try:
        with urllib.request.urlopen(SPRING_METADATA_URL, timeout=10) as response:
            import json
            data = json.load(response)
    except (urllib.error.URLError, urllib.error.HTTPError):
        # 조회 실패 시 폴백
        return []

    versions = data.get("bootVersion", {}).get("values", [])
    # RELEASE 버전만 (SNAPSHOT 제외), .RELEASE 접미사 제거
    release_versions = []
    for v in versions:
        version_id = v["id"]
        if "SNAPSHOT" in version_id:
            continue
        # ".RELEASE" 제거
        if version_id.endswith(".RELEASE"):
            version_id = version_id[:-len(".RELEASE")]
        release_versions.append(version_id)
    return release_versions

def cmd_init_spring_boot():
    """stoke init spring-boot 명령어."""
    print("Creating Spring Boot project via start.spring.io\n")

    cwd = Path.cwd()
    is_empty = not any(cwd.iterdir())

    if is_empty:
        default_name = cwd.name
        project_name = _prompt("Project name", default_name)
    else:
        project_name = _prompt("Project name", "myapp")

    group_id = _prompt("Group ID (e.g. com.example)", "com.example")

    # Spring Boot 버전 조회
    print("Fetching available Spring Boot versions...")
    available_versions = _fetch_boot_versions()

    if available_versions:
        print(f"\nAvailable Spring Boot versions:")
        for i, v in enumerate(available_versions):
            marker = " (latest)" if i == 0 else ""
            print(f"  {i+1}. {v}{marker}")

        choice_str = _prompt(f"Select version (1-{len(available_versions)})", "1")
        try:
            choice = int(choice_str) - 1
            if 0 <= choice < len(available_versions):
                boot_version = available_versions[choice]
            else:
                boot_version = available_versions[0]
        except ValueError:
            boot_version = available_versions[0]
    else:
        # API 조회 실패 시 수동 입력
        print("Could not fetch versions. Enter manually.")
        boot_version = _prompt("Spring Boot version", "4.1.0.RELEASE")

    print(f"Using Spring Boot: {boot_version}\n")
    java_choices = ["17", "21", "25"]
    java_idx = _prompt_choice("Java version", java_choices, default_index=1)
    java_version = java_choices[java_idx]

    build_tool_idx = _prompt_choice("Build tool", ["maven", "gradle"], default_index=0)
    build_tool = ["maven-project", "gradle-project"][build_tool_idx]

    packaging_idx = _prompt_choice("Packaging", ["jar", "war"], default_index=0)
    packaging = ["jar", "war"][packaging_idx]

    print("\nCommon dependencies:")
    print("  web           - Spring Web (REST API)")
    print("  data-jpa      - Spring Data JPA")
    print("  security      - Spring Security")
    print("  actuator      - Spring Boot Actuator")
    print("  devtools      - Spring Boot DevTools")
    print("  lombok        - Lombok")
    print("  h2            - H2 Database")
    print("  postgresql    - PostgreSQL Driver")

    deps_input = _prompt("Dependencies (comma-separated, empty for none)", "web")
    dependencies = deps_input.strip()

    # 다운로드 요청
    params = {
        "type": build_tool,
        "language": "java",
        "bootVersion": boot_version,
        "baseDir": "." if is_empty else project_name,
        "groupId": group_id,
        "artifactId": project_name,
        "name": project_name,
        "packageName": f"{group_id}.{project_name}",
        "packaging": packaging,
        "javaVersion": java_version,
    }
    if dependencies:
        params["dependencies"] = dependencies

    query = urllib.parse.urlencode(params)
    url = f"{SPRING_INITIALIZR_URL}?{query}"

    print(f"\nDownloading from start.spring.io...")

    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            zip_data = response.read()
    except urllib.error.HTTPError as e:
        print(f"Error: HTTP {e.code}: {e.reason}", file=sys.stderr)
        if e.code == 400:
            print("Check Spring Boot version and dependencies.", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Error: network error: {e}", file=sys.stderr)
        sys.exit(1)

    # 압축 해제
    dest_dir = Path.cwd()
    if is_empty:
        project_path = dest_dir
    else:
        project_path = dest_dir / project_name

    print(f"Extracting to {project_path}...")

    try:
        with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
            zf.extractall(dest_dir)
    except zipfile.BadZipFile:
        print("Error: invalid zip file received", file=sys.stderr)
        sys.exit(1)

    print(f"\nSpring Boot project created at: {project_path}")
    print()
    print("Next steps:")
    print(f"  cd {project_name}")

    if build_tool == "maven-project":
        print(f"  mvnw spring-boot:run    (Linux/macOS)")
        print(f"  mvnw.cmd spring-boot:run  (Windows)")
    else:
        print(f"  gradlew bootRun         (Linux/macOS)")
        print(f"  gradlew.bat bootRun     (Windows)")

    print()
    print("Open in IDE:")
    print(f"  IntelliJ: File -> Open -> {project_name}/")
    print(f"  VSCode:   code {project_name}/")

def _prompt(question: str, default: str | None = None) -> str:
    """간단한 입력 프롬프트."""
    if default:
        prompt = f"{question} [{default}]: "
    else:
        prompt = f"{question}: "

    while True:
        try:
            value = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            sys.exit(1)

        if value:
            return value
        if default is not None:
            return default
        print("Value required.")

def _prompt_choice(question: str, choices: list[str], default_index: int = 0) -> int:
    """선택지 프롬프트. 인덱스 반환."""
    choice_str = "/".join(choices)
    prompt = f"{question} [{choice_str}] [{choices[default_index]}]: "

    while True:
        try:
            value = input(prompt).strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            sys.exit(1)

        if not value:
            return default_index

        for i, choice in enumerate(choices):
            if value == choice.lower():
                return i

        print(f"Invalid choice. Choose from: {choice_str}")