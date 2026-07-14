"""
IntelliJ IDEA 등 자바 IDE용 pom.xml 자동 생성.
Maven 설치 없이도 IDE가 이 파일을 읽어서 프로젝트 구조를 파악함.
"""

from pathlib import Path
from xml.sax.saxutils import escape

def _relative_path(path: Path, project_root: Path) -> str:
    """project_root 기준 상대 경로. 실패 시 절대 경로."""
    try:
        return str(path.relative_to(project_root)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")

def generate_pom(
    project_name: str,
    project_version: str,
    java_version: str,
    source_dirs: list[Path],
    output_dir: Path,
    deps: dict[str, str],
    project_root: Path,
) -> str:
    """
    pom.xml 내용 생성.

    project_name: stoke 프로젝트 이름 (Maven artifactId로 사용)
    project_version: 프로젝트 버전 (예: "0.1.0")
    java_version: 자바 메이저 버전 (예: "25")
    source_dirs: 소스 폴더 목록
    output_dir: 컴파일 결과 폴더 (Maven target 대체)
    deps: {"groupId:artifactId": "version"}
    """
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append(
        '<project xmlns="http://maven.apache.org/POM/4.0.0" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 '
        'https://maven.apache.org/xsd/maven-4.0.0.xsd">'
    )
    lines.append('    <modelVersion>4.0.0</modelVersion>')
    lines.append('')

    # 프로젝트 정보
    lines.append(f'    <groupId>stoke.local</groupId>')
    lines.append(f'    <artifactId>{escape(project_name)}</artifactId>')
    lines.append(f'    <version>{escape(project_version)}</version>')
    lines.append('    <packaging>jar</packaging>')
    lines.append('')

    # 자바 버전
    lines.append('    <properties>')
    lines.append(f'        <maven.compiler.source>{escape(java_version)}</maven.compiler.source>')
    lines.append(f'        <maven.compiler.target>{escape(java_version)}</maven.compiler.target>')
    lines.append('        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>')
    lines.append('    </properties>')
    lines.append('')

    # 소스/출력 경로
    lines.append('    <build>')
    if source_dirs:
        # Maven은 단일 sourceDirectory만 지원
        first_source = _relative_path(source_dirs[0], project_root)
        lines.append(f'        <sourceDirectory>{escape(first_source)}</sourceDirectory>')

    output_path = _relative_path(output_dir, project_root)
    lines.append(f'        <outputDirectory>{escape(output_path)}</outputDirectory>')
    lines.append('    </build>')
    lines.append('')

    # 의존성
    if deps:
        lines.append('    <dependencies>')
        for name, version in deps.items():
            if ":" not in name:
                continue
            group_id, artifact_id = name.split(":", 1)
            lines.append('        <dependency>')
            lines.append(f'            <groupId>{escape(group_id)}</groupId>')
            lines.append(f'            <artifactId>{escape(artifact_id)}</artifactId>')
            lines.append(f'            <version>{escape(version)}</version>')
            lines.append('        </dependency>')
        lines.append('    </dependencies>')
        lines.append('')

    lines.append('</project>')
    return "\n".join(lines) + "\n"

def write_pom(
    project_root: Path,
    project_name: str,
    project_version: str,
    java_version: str,
    source_dirs: list[Path],
    output_dir: Path,
    deps: dict[str, str],
) -> tuple[Path, bool]:
    """
    pom.xml을 프로젝트 루트에 저장.
    반환: (파일 경로, 실제 변경 여부)
    """
    pom_content = generate_pom(
        project_name=project_name,
        project_version=project_version,
        java_version=java_version,
        source_dirs=source_dirs,
        output_dir=output_dir,
        deps=deps,
        project_root=project_root,
    )
    pom_path = project_root / "pom.xml"

    if pom_path.exists():
        old_content = pom_path.read_text(encoding="utf-8")
        if old_content == pom_content:
            return pom_path, False

    pom_path.write_text(pom_content, encoding="utf-8")
    return pom_path, True