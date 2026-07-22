"""
C 전용 라이브러리 목록.
언어 호환성 검증에 사용.

원칙:
- 이 목록에 있으면 C 전용 라이브러리로 판단
- 이 목록에 없으면 C++ 라이브러리로 간주 (안전한 default)
- C 라이브러리는 C++ 프로젝트에서도 사용 가능 (extern "C")
- C++ 라이브러리는 C 프로젝트에서 사용 불가
"""


# vcpkg에서 자주 사용되는 C 라이브러리들
C_ONLY_LIBRARIES = {
    # 압축
    "zlib",
    "bzip2",
    "xz-utils",
    "zstd",
    "lz4",

    # 암호화
    "openssl",

    # 네트워킹
    "curl",
    "libssh",
    "libssh2",
    "libwebsockets",

    # 데이터베이스
    "sqlite3",
    "libpq",  # PostgreSQL
    "hiredis",  # Redis

    # 파싱
    "libxml2",
    "expat",
    "yajl",  # JSON
    "libyaml",

    # 그래픽/이미지
    "libpng",
    "libjpeg-turbo",
    "libtiff",
    "libwebp",
    "giflib",
    "libgif",

    # 오디오
    "libogg",
    "libvorbis",
    "libflac",
    "libmpg123",

    # 비디오
    "ffmpeg",
    "libvpx",

    # 시스템
    "libusb",
    "libuv",
    "libevent",
    "libarchive",

    # 국제화
    "libiconv",
    "gettext",

    # 폰트/렌더링
    "freetype",
    "harfbuzz",

    # 정규식
    "pcre2",
    "pcre",

    # 기타
    "libffi",
    "libtool",
    "readline",
    "ncurses",
}

def is_c_library(name: str) -> bool:
    """
    라이브러리 이름이 C 전용 라이브러리인지 확인.
    반환: True면 C 라이브러리 (C/C++ 프로젝트 모두 사용 가능)
    """
    return name.lower() in C_ONLY_LIBRARIES

def can_use_in_c_project(name: str) -> bool:
    """
    C 프로젝트에서 이 라이브러리를 사용할 수 있는지.
    C 라이브러리만 가능. 모르는 라이브러리는 C++로 간주해서 불가.
    """
    return is_c_library(name)

def can_use_in_cpp_project(name: str) -> bool:
    """
    C++ 프로젝트에서 이 라이브러리를 사용할 수 있는지.
    C, C++ 라이브러리 모두 가능.
    """
    return True