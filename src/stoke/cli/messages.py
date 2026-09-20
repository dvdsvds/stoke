"""CLI 메시지 다국어 지원."""
import os


MESSAGES = {
    "en": {
        # stoke
        "prog.description": "Build, scaffold, and manage toolchains/dependencies for multi-language projects",

        # build
        "build.help": "Build a target",
        "build.target": "Target name",
        "build.force": "Ignore cache and rebuild everything",
        "build.all": "Build every member of the workspace (run at a workspace root created with 'stoke init --workspace')",
        "build.debug": "Debug build (default): -O0 -g, easy to debug",
        "build.release": "Release build: -O2, optimized for deployment",
        "build.profile": "Custom build profile name (defined in stoke.toml)",
        "build.verbose": "Show detailed build output",

        # python/java/c/cpp tools
        "python.help": "Python version tools",
        "python.list.help": "List installed Python versions",
        "java.help": "Java (JDK) version tools",
        "java.list.help": "List installed JDKs",
        "c.help": "C compiler tools",
        "c.list.help": "List installed C compilers",
        "cpp.help": "C++ compiler tools",
        "cpp.list.help": "List installed C++ compilers",

        # install/uninstall
        "install.help": "Install a language toolchain or vcpkg",
        "install.tool": "Language to install, or 'vcpkg'",
        "uninstall.help": "Uninstall a language toolchain or vcpkg",
        "uninstall.tool": "Language to uninstall, or 'vcpkg'",

        # vcpkg
        "vcpkg.help": "vcpkg library management",
        "vcpkg.install.help": "Install a library",
        "vcpkg.install.library": "Library name",
        "vcpkg.install.version": "Specific version (default: latest)",
        "vcpkg.install.target": "Target name in stoke.toml",
        "vcpkg.remove.help": "Remove a library",
        "vcpkg.remove.library": "Library name",
        "vcpkg.remove.target": "Target name in stoke.toml",
        "vcpkg.list.help": "List installed libraries",
        "vcpkg.list.target": "Target name in stoke.toml",
        "vcpkg.version.help": "Show installed vcpkg version",

        # clean
        "clean.help": "Clean build artifacts",
        "clean.all": "Also delete lock file (full reset)",
        "clean.target": "Target name (default: all targets)",

        # init
        "init.help": "Initialize a new stoke project",

        # watch
        "watch.help": "Watch for file changes and rebuild automatically",
        "watch.target": "Target name",
        "watch.debug": "Debug build (default, C/C++ only)",
        "watch.release": "Release build (C/C++ only)",
        "watch.profile": "Custom build profile name (C/C++ only)",
        "watch.verbose": "Show detailed build output",

        # run
        "run.help": "Run the built target (Python: entry file, Java: main_class)",
        "run.target": "Target name",
        "run.entry_file": "Run this file instead of the target's configured entry (Python/JS/TS/Ruby/PHP only)",
        "run.debug": "Run debug build (default, C/C++ only)",
        "run.release": "Run release build (C/C++ only)",
        "run.profile": "Run specific custom profile build (C/C++ only)",

        # ide-sync
        "ide-sync.help": "Scan for stoke projects and generate workspace .vscode/settings.json",

        # hot-reload
        "hot-reload.help": "Watch, rebuild, and restart the running process on changes",
        "hot-reload.target": "Target name",
        "hot-reload.debug": "Debug build (default, C/C++ only)",
        "hot-reload.release": "Release build (C/C++ only)",
        "hot-reload.profile": "Custom build profile name (C/C++ only)",
        "hot-reload.verbose": "Show detailed build output",

        # test
        "test.help": "Run the target's tests (pytest, go test, cargo test, ctest, meson test, etc. depending on language)",
        "test.target": "Target name",
        "test.debug": "Use the debug build's test output directory (C/C++ only)",
        "test.release": "Use the release build's test output directory (C/C++ only)",
        "test.profile": "Custom build profile name (C/C++ only)",
        "test.verbose": "Show detailed test output",
        "test.all": "Test every member of the workspace (run at a workspace root created with 'stoke init --workspace')",

        # add/remove
        "add.help": "Add a dependency to a Python/Java target's stoke.toml and install it",
        "add.package": "Package name (pip package, or 'groupId:artifactId' for Java)",
        "add.version": "Version (optional for Python, required for Java)",
        "add.target": "Target name (default: first target)",
        "remove.help": "Remove a dependency from a Python/Java target's stoke.toml",
        "remove.package": "Package name",
        "remove.target": "Target name (default: first target)",

        # exec
        "exec.help": "Run a command with the target's project-local toolchain on PATH (e.g. 'stoke exec -- go mod tidy')",
        "exec.command": "Command to run (put -- before it to separate from stoke's own flags)",
        "exec.target": "Target name (default: first target)",

        # audit
        "audit.help": "Check the target's dependencies for known vulnerabilities (CVEs)",
        "audit.target": "Target name (default: first target)",
        "audit.json": "Print machine-readable JSON instead of human-readable text (structured for Python/Java/JS/TS/PHP; wraps the native tool's raw output for the rest)",

        # outdated
        "outdated.help": "Check the target's dependencies against the latest available version (staleness, not CVEs)",
        "outdated.target": "Target name (default: first target)",
        "outdated.json": "Print machine-readable JSON instead of human-readable text (structured for Python/Java/JS/TS/PHP; wraps the native tool's raw output for the rest)",

        # sbom
        "sbom.help": "Generate a Software Bill of Materials (SBOM) for the target's dependencies",
        "sbom.target": "Target name (default: first target)",
        "sbom.format": "SBOM format: 'cyclonedx' (default) or 'spdx'",
        "sbom.output": "Output file path, or '-' for stdout (default: sbom.cdx.json / sbom.spdx.json in the project root)",

        # doctor
        "doctor.help": "Diagnose the target's environment (toolchain, lock file, venv) without building anything",
        "doctor.target": "Target name (default: first target)",
        "doctor.json": "Print machine-readable JSON instead of human-readable text",

        # self-update
        "self-update.help": "Update the standalone stoke binary to the latest release",
        "self-update.check": "Only check whether a newer version is available, don't install it",
        "self-update.yes": "Don't prompt for confirmation before updating",

        # completions
        "completions.help": "Print a shell completion script for bash/zsh/fish",
        "completions.shell": "Shell to generate a completion script for",

        # git
        "git.help": "Interactive menu to add/commit/push (requires an existing git repo)",

        # new
        "new.help": "Create a new service as its own subdirectory (for a monorepo -- adds it to the workspace's members if run inside one)",
        "new.name": "Service name (also the subdirectory name)",
        "new.language": "Language, e.g. -l python",
        "new.version": "Language version/standard/toolchain pin (meaning depends on language)",
        "new.env_type": "Python environment type (default venv)",
        "new.lock_mode": "Lock file mode (default commit)",
        "new.vcpkg": "Install vcpkg for C/C++ if not already installed",
    },
    "ko": {
        # stoke
        "prog.description": "다중 언어 프로젝트 빌드·스캐폴딩·툴체인/의존성 관리 툴",

        # build
        "build.help": "타겟 빌드",
        "build.target": "타겟 이름",
        "build.force": "캐시 무시하고 전체 재빌드",
        "build.all": "워크스페이스의 모든 멤버 빌드 ('stoke init --workspace'로 만든 워크스페이스 루트에서 실행)",
        "build.debug": "Debug 빌드 (기본): -O0 -g, 디버깅 편함",
        "build.release": "Release 빌드: -O2, 배포용 최적화",
        "build.profile": "커스텀 빌드 프로파일 이름 (stoke.toml에서 정의)",
        "build.verbose": "상세 빌드 출력 표시",

        # python/java/c/cpp tools
        "python.help": "Python 버전 도구",
        "python.list.help": "설치된 Python 버전 목록",
        "java.help": "Java (JDK) 버전 도구",
        "java.list.help": "설치된 JDK 목록",
        "c.help": "C 컴파일러 도구",
        "c.list.help": "설치된 C 컴파일러 목록",
        "cpp.help": "C++ 컴파일러 도구",
        "cpp.list.help": "설치된 C++ 컴파일러 목록",

        # install/uninstall
        "install.help": "언어 툴체인 또는 vcpkg 설치",
        "install.tool": "설치할 언어, 또는 'vcpkg'",
        "uninstall.help": "언어 툴체인 또는 vcpkg 제거",
        "uninstall.tool": "제거할 언어, 또는 'vcpkg'",

        # vcpkg
        "vcpkg.help": "vcpkg 라이브러리 관리",
        "vcpkg.install.help": "라이브러리 설치",
        "vcpkg.install.library": "라이브러리 이름",
        "vcpkg.install.version": "특정 버전 (기본: 최신)",
        "vcpkg.install.target": "stoke.toml의 타겟 이름",
        "vcpkg.remove.help": "라이브러리 제거",
        "vcpkg.remove.library": "라이브러리 이름",
        "vcpkg.remove.target": "stoke.toml의 타겟 이름",
        "vcpkg.list.help": "설치된 라이브러리 목록",
        "vcpkg.list.target": "stoke.toml의 타겟 이름",
        "vcpkg.version.help": "설치된 vcpkg 버전 표시",

        # clean
        "clean.help": "빌드 산출물 정리",
        "clean.all": "lock 파일도 삭제 (전체 초기화)",
        "clean.target": "타겟 이름 (기본: 모든 타겟)",

        # init
        "init.help": "새 stoke 프로젝트 초기화",

        # watch
        "watch.help": "파일 변경 감시 및 자동 재빌드",
        "watch.target": "타겟 이름",
        "watch.debug": "Debug 빌드 (기본, C/C++ 전용)",
        "watch.release": "Release 빌드 (C/C++ 전용)",
        "watch.profile": "커스텀 빌드 프로파일 이름 (C/C++ 전용)",
        "watch.verbose": "상세 빌드 출력 표시",

        # run
        "run.help": "빌드된 타겟 실행 (Python: entry 파일, Java: main_class)",
        "run.target": "타겟 이름",
        "run.entry_file": "타겟에 설정된 entry 대신 이 파일을 실행 (Python/JS/TS/Ruby/PHP 전용)",
        "run.debug": "Debug 빌드 실행 (기본, C/C++ 전용)",
        "run.release": "Release 빌드 실행 (C/C++ 전용)",
        "run.profile": "특정 커스텀 프로파일 빌드 실행 (C/C++ 전용)",

        # ide-sync
        "ide-sync.help": "stoke 프로젝트 스캔 및 워크스페이스 .vscode/settings.json 생성",

        # hot-reload
        "hot-reload.help": "감시, 재빌드, 실행 프로세스 재시작",
        "hot-reload.target": "타겟 이름",
        "hot-reload.debug": "Debug 빌드 (기본, C/C++ 전용)",
        "hot-reload.release": "Release 빌드 (C/C++ 전용)",
        "hot-reload.profile": "커스텀 빌드 프로파일 이름 (C/C++ 전용)",
        "hot-reload.verbose": "상세 빌드 출력 표시",

        # test
        "test.help": "타겟의 테스트 실행 (언어에 따라 pytest, go test, cargo test, ctest, meson test 등)",
        "test.target": "타겟 이름",
        "test.debug": "Debug 빌드의 테스트 출력 디렉토리 사용 (C/C++ 전용)",
        "test.release": "Release 빌드의 테스트 출력 디렉토리 사용 (C/C++ 전용)",
        "test.profile": "커스텀 빌드 프로파일 이름 (C/C++ 전용)",
        "test.verbose": "상세 테스트 출력 표시",
        "test.all": "워크스페이스의 모든 멤버 테스트 ('stoke init --workspace'로 만든 워크스페이스 루트에서 실행)",

        # add/remove
        "add.help": "Python/Java 타겟의 stoke.toml에 의존성 추가 후 설치",
        "add.package": "패키지 이름 (pip 패키지, Java는 'groupId:artifactId')",
        "add.version": "버전 (Python은 선택, Java는 필수)",
        "add.target": "타겟 이름 (기본값: 첫 번째 타겟)",
        "remove.help": "Python/Java 타겟의 stoke.toml에서 의존성 제거",
        "remove.package": "패키지 이름",
        "remove.target": "타겟 이름 (기본값: 첫 번째 타겟)",

        # exec
        "exec.help": "타겟의 프로젝트 로컬 툴체인을 PATH에 얹은 채로 명령 실행 (예: 'stoke exec -- go mod tidy')",
        "exec.command": "실행할 명령 (stoke 자체 플래그와 구분하려면 앞에 -- 를 붙일 것)",
        "exec.target": "타겟 이름 (기본값: 첫 번째 타겟)",

        # audit
        "audit.help": "타겟의 의존성을 알려진 취약점(CVE)과 대조 확인",
        "audit.target": "타겟 이름 (기본값: 첫 번째 타겟)",
        "audit.json": "사람이 읽는 텍스트 대신 기계가 읽는 JSON 출력 (Python/Java/JS/TS/PHP는 구조화됨, 나머지는 네이티브 도구의 원본 출력을 감싸서 반환)",

        # outdated
        "outdated.help": "타겟의 의존성이 최신 버전 대비 얼마나 뒤처졌는지 확인 (CVE와는 별개)",
        "outdated.target": "타겟 이름 (기본값: 첫 번째 타겟)",
        "outdated.json": "사람이 읽는 텍스트 대신 기계가 읽는 JSON 출력 (Python/Java/JS/TS/PHP는 구조화됨, 나머지는 네이티브 도구의 원본 출력을 감싸서 반환)",

        # sbom
        "sbom.help": "타겟 의존성의 SBOM(소프트웨어 부품 명세) 생성",
        "sbom.target": "타겟 이름 (기본값: 첫 번째 타겟)",
        "sbom.format": "SBOM 포맷: 'cyclonedx'(기본값) 또는 'spdx'",
        "sbom.output": "출력 파일 경로, '-'면 표준출력 (기본값: 프로젝트 루트의 sbom.cdx.json / sbom.spdx.json)",

        # doctor
        "doctor.help": "아무것도 빌드하지 않고 타겟 환경(툴체인, lock 파일, venv) 진단",
        "doctor.target": "타겟 이름 (기본값: 첫 번째 타겟)",
        "doctor.json": "사람이 읽는 텍스트 대신 기계가 읽는 JSON 출력",

        # self-update
        "self-update.help": "단일 실행 파일 배포판 stoke를 최신 릴리스로 업데이트",
        "self-update.check": "새 버전이 있는지 확인만 하고 설치는 안 함",
        "self-update.yes": "업데이트 전 확인 프롬프트 생략",

        # completions
        "completions.help": "bash/zsh/fish용 셸 자동완성 스크립트 출력",
        "completions.shell": "자동완성 스크립트를 생성할 셸",

        # git
        "git.help": "add/commit/push 대화형 메뉴 (기존 git 저장소 필요)",

        # new
        "new.help": "새 서비스를 독립된 서브디렉토리로 생성 (모노레포용 -- 워크스페이스 안에서 실행하면 members에 자동 추가)",
        "new.name": "서비스 이름 (서브디렉토리 이름으로도 씀)",
        "new.language": "언어, 예: -l python",
        "new.version": "언어 버전/표준/툴체인 pin (의미는 언어마다 다름)",
        "new.env_type": "Python 환경 타입 (기본값 venv)",
        "new.lock_mode": "Lock 파일 모드 (기본값 commit)",
        "new.vcpkg": "C/C++용 vcpkg가 없으면 설치",
    },
}

def get_message(key: str) -> str:
    """환경변수 STOKE_LANG에 따라 언어별 메시지 반환."""
    lang = os.getenv("STOKE_LANG", "en")
    if lang not in MESSAGES:
        lang = "en"
    return MESSAGES[lang].get(key, MESSAGES["en"].get(key, key))