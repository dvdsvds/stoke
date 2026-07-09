"""
stoke.toml 파일을 수정하기 위한 유틸리티.
tomllib은 읽기 전용이라 정규식으로 섹션을 찾아서 수정.
주석이랑 원본 순서 유지 목표.
"""

import re
from pathlib import Path


def add_dep(toml_path: Path, target_name: str, lib_name: str, version: str) -> None:
    """
    stoke.toml의 [targets.<target_name>.deps] 섹션에 라이브러리 추가.
    섹션이 없으면 만들어요.
    이미 있으면 버전만 업데이트.
    """
    content = toml_path.read_text(encoding="utf-8")
    section_header = f"[targets.{target_name}.deps]"

    # 섹션이 있는지 찾기
    section_match = re.search(
        r"^\[targets\." + re.escape(target_name) + r"\.deps\]\s*$",
        content,
        re.MULTILINE,
    )

    if section_match is None:
        # 섹션 없으면 파일 끝에 추가
        if not content.endswith("\n"):
            content += "\n"
        content += f"\n{section_header}\n{lib_name} = \"{version}\"\n"
        toml_path.write_text(content, encoding="utf-8")
        return

    # 섹션 있으면 섹션 안에 라인 추가/수정
    section_start = section_match.end()
    # 다음 섹션 시작 위치 찾기
    next_section_match = re.search(
        r"^\[",
        content[section_start:],
        re.MULTILINE,
    )
    if next_section_match:
        section_end = section_start + next_section_match.start()
    else:
        section_end = len(content)

    section_body = content[section_start:section_end]

    # 이미 있는 라이브러리인지 확인
    lib_pattern = re.compile(
        r"^(" + re.escape(lib_name) + r")\s*=\s*\".*?\"\s*$",
        re.MULTILINE,
    )

    if lib_pattern.search(section_body):
        # 버전 업데이트
        new_section_body = lib_pattern.sub(
            f'{lib_name} = "{version}"',
            section_body,
        )
    else:
        # 새 라인 추가 (섹션 끝에)
        # 마지막 non-empty line 다음에 추가
        section_body_stripped = section_body.rstrip("\n")
        if section_body_stripped:
            new_section_body = section_body_stripped + f"\n{lib_name} = \"{version}\"\n"
        else:
            new_section_body = f"\n{lib_name} = \"{version}\"\n"

        # 다음 섹션 전에 빈 줄 하나 유지
        if next_section_match:
            new_section_body += "\n"

    content = content[:section_start] + new_section_body + content[section_end:]
    toml_path.write_text(content, encoding="utf-8")


def remove_dep(toml_path: Path, target_name: str, lib_name: str) -> bool:
    """
    stoke.toml의 [targets.<target_name>.deps] 섹션에서 라이브러리 제거.
    반환: 제거 성공하면 True, 라이브러리 없으면 False.
    """
    content = toml_path.read_text(encoding="utf-8")

    # 섹션 찾기
    section_match = re.search(
        r"^\[targets\." + re.escape(target_name) + r"\.deps\]\s*$",
        content,
        re.MULTILINE,
    )

    if section_match is None:
        return False

    section_start = section_match.end()
    next_section_match = re.search(
        r"^\[",
        content[section_start:],
        re.MULTILINE,
    )
    if next_section_match:
        section_end = section_start + next_section_match.start()
    else:
        section_end = len(content)

    section_body = content[section_start:section_end]

    # 라이브러리 라인 찾아서 제거
    lib_pattern = re.compile(
        r"^" + re.escape(lib_name) + r"\s*=\s*\".*?\"\s*\n",
        re.MULTILINE,
    )

    if not lib_pattern.search(section_body):
        return False

    new_section_body = lib_pattern.sub("", section_body)

    content = content[:section_start] + new_section_body + content[section_end:]
    toml_path.write_text(content, encoding="utf-8")
    return True


def list_deps(toml_path: Path, target_name: str) -> dict[str, str]:
    """
    stoke.toml의 [targets.<target_name>.deps] 섹션의 라이브러리 목록.
    반환: {이름: 버전} 딕셔너리.
    """
    content = toml_path.read_text(encoding="utf-8")

    section_match = re.search(
        r"^\[targets\." + re.escape(target_name) + r"\.deps\]\s*$",
        content,
        re.MULTILINE,
    )

    if section_match is None:
        return {}

    section_start = section_match.end()
    next_section_match = re.search(
        r"^\[",
        content[section_start:],
        re.MULTILINE,
    )
    if next_section_match:
        section_end = section_start + next_section_match.start()
    else:
        section_end = len(content)

    section_body = content[section_start:section_end]

    deps = {}
    for match in re.finditer(
        r"^([\w-]+)\s*=\s*\"(.*?)\"\s*$",
        section_body,
        re.MULTILINE,
    ):
        deps[match.group(1)] = match.group(2)

    return deps