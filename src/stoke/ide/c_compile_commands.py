"""
C/C++ IDE 통합용 compile_commands.json 자동 생성.
VSCode C/C++ 확장, clangd, CLion 등 대부분 C/C++ IDE가 이 파일을 인식함.
"""

import json
from pathlib import Path


def generate_compile_commands(
    compiler_path: Path,
    source_files: list[Path],
    project_root: Path,
    objects_dir: Path,
    include_dirs: list[Path],
    standard: str | None = None,
    standard_flag_prefix: str = "-std=",
) -> list[dict]:
    """
    compile_commands.json 데이터 생성.
    반환: JSON 배열이 될 dict 리스트.
    """
    commands = []

    for source in source_files:
        # 컴파일 명령어 조합 (실제 컴파일 로직이랑 동일)
        cmd_parts = [str(compiler_path)]

        # 표준
        if standard:
            cmd_parts.append(f"{standard_flag_prefix}{standard}")

        # Include 경로
        for include in include_dirs:
            cmd_parts.append(f"-I{include}")

        # 오브젝트 파일 경로
        try:
            rel_source = source.relative_to(project_root)
        except ValueError:
            rel_source = Path(source.name)
        obj_path = objects_dir / rel_source.with_suffix(".o")

        # 컴파일만 (링크 X)
        cmd_parts.append("-c")
        cmd_parts.append(str(source))
        cmd_parts.append("-o")
        cmd_parts.append(str(obj_path))

        commands.append({
            "directory": str(project_root).replace("\\", "/"),
            "file": str(source).replace("\\", "/"),
            "command": " ".join(cmd_parts).replace("\\", "/"),
        })

    return commands


def write_compile_commands(
    project_root: Path,
    compiler_path: Path,
    source_files: list[Path],
    objects_dir: Path,
    include_dirs: list[Path],
    standard: str | None = None,
    standard_flag_prefix: str = "-std=",
) -> Path:
    """
    프로젝트 루트에 compile_commands.json 저장.
    반환: 저장된 파일 경로.
    """
    commands = generate_compile_commands(
        compiler_path=compiler_path,
        source_files=source_files,
        project_root=project_root,
        objects_dir=objects_dir,
        include_dirs=include_dirs,
        standard=standard,
        standard_flag_prefix=standard_flag_prefix,
    )

    output_path = project_root / "compile_commands.json"
    output_path.write_text(
        json.dumps(commands, indent=2) + "\n",
        encoding="utf-8",
    )
    return output_path