"""C/C++ 컴파일러가 생성한 .d 파일 (헤더 의존성 파일) 파싱."""
from pathlib import Path

def parse_dep_file(dep_path: Path) -> list[Path]:
    """
    gcc가 생성한 .d 파일 파싱해서 헤더 파일 목록 반환.
    .d 파일 형식:
        target.o: source.c \
         header1.h \
         header2.h
    소스 파일은 제외하고 헤더만 반환.
    """
    if not dep_path.exists():
        return []
    try:
        content = dep_path.read_text(encoding="utf-8")
    except OSError:
        return []
    # 라인 이어붙이기 (백슬래시 + 개행)
    content = content.replace("\\\n", " ")
    # 첫 번째 콜론 찾기 (target.o:)
    colon_idx = content.find(":")
    if colon_idx == -1:
        return []
    # 콜론 이후가 의존성 목록
    deps_str = content[colon_idx + 1:]
    # 공백으로 분리
    tokens = deps_str.split()
    # 첫 번째는 소스 파일 (skip), 나머지가 헤더
    if len(tokens) < 2:
        return []
    headers = []
    for token in tokens[1:]:
        token = token.strip()
        if token:
            headers.append(Path(token))
    return headers