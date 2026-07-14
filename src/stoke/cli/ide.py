"""ide-sync 명령어."""
from pathlib import Path
import tomllib


def cmd_ide_sync():
    from stoke.ide.vscode import (
        find_stoke_projects,
        make_workspace_settings,
        write_project_settings,
        make_workspace_file,
        write_workspace_file,
    )

    root = Path.cwd()
    print(f"Scanning for stoke projects under {root}...")
    projects = find_stoke_projects(root)

    if not projects:
        print("No stoke projects found.")
        workspace_name = root.name
        workspace_path = root / f"{workspace_name}.code-workspace"
        if workspace_path.exists():
            workspace_path.unlink()
            print(f"Removed: {workspace_path}")
        return

    print(f"Found {len(projects)} project(s):")

    projects_by_language = {}
    for project_path in projects:
        stoke_toml = project_path / "stoke.toml"
        try:
            with open(stoke_toml, "rb") as f:
                data = tomllib.load(f)
        except (OSError, tomllib.TOMLDecodeError) as e:
            print(f"  Skipping {project_path.name} (invalid stoke.toml): {e}")
            continue

        targets = data.get("targets", {})
        if not targets:
            print(f"  Skipping {project_path.name} (no targets)")
            continue

        first_target = next(iter(targets.values()))
        language = first_target.get("language")
        if not language:
            print(f"  Skipping {project_path.name} (no language)")
            continue

        try:
            rel_path = project_path.relative_to(root)
        except ValueError:
            rel_path = project_path

        print(f"  [{language}] {rel_path}")

        if language not in projects_by_language:
            projects_by_language[language] = []

        if language == "python":
            projects_by_language[language].append({
                "absolute": project_path,
                "relative": rel_path,
            })
        else:
            projects_by_language[language].append(rel_path)

    # 워크스페이스 설정 생성
    settings = make_workspace_settings(projects_by_language)
    if settings:
        settings_path, _ = write_project_settings(root, settings)
        print(f"\nGenerated: {settings_path}")

    # multi-root workspace 파일 생성
    workspace_content = make_workspace_file(projects, root)
    workspace_path = write_workspace_file(root, workspace_content)
    print(f"Generated: {workspace_path}")
    print(f"\nOpen in VSCode: {workspace_path}")