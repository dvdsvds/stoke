"""CLI 메시지 다국어 지원."""
import os


MESSAGES = {
    "en": {
        # stoke
        "prog.description": "A build tool for multiple languages",

        # build
        "build.help": "Build a target",
        "build.target": "Target name",
        "build.force": "Ignore cache and rebuild everything",
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
        "install.help": "Install a tool (vcpkg, ...)",
        "install.tool": "Tool to install",
        "uninstall.help": "Uninstall a tool (vcpkg, ...)",
        "uninstall.tool": "Tool to uninstall",

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
    },
    "ko": {
        # stoke
        "prog.description": "다중 언어 빌드 툴",

        # build
        "build.help": "타겟 빌드",
        "build.target": "타겟 이름",
        "build.force": "캐시 무시하고 전체 재빌드",
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
        "install.help": "도구 설치 (vcpkg, ...)",
        "install.tool": "설치할 도구",
        "uninstall.help": "도구 제거 (vcpkg, ...)",
        "uninstall.tool": "제거할 도구",

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
    },
}

def get_message(key: str) -> str:
    """환경변수 STOKE_LANG에 따라 언어별 메시지 반환."""
    lang = os.getenv("STOKE_LANG", "en")
    if lang not in MESSAGES:
        lang = "en"
    return MESSAGES[lang].get(key, MESSAGES["en"].get(key, key))