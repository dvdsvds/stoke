"""JavaScript 프로젝트 초기화 로직."""
from pathlib import Path

def _write_stoke_toml_javascript(
    path: Path,
    project_name: str,
    lock_mode: str,
) -> None:
    """JavaScript 프로젝트용 stoke.toml 쓰기."""
    content = f'''[project]
name = "{project_name}"
version = "0.1.0"
lock_mode = "{lock_mode}"

[targets.{project_name}]
language = "javascript"
entry = "src/main.js"
'''
    path.write_text(content, encoding="utf-8")

def _write_example_javascript(project_root: Path) -> None:
    """JavaScript 예시 파일 생성."""
    src = project_root / "src"
    src.mkdir(exist_ok=True)
    main_js = src / "main.js"
    if main_js.exists():
        return

    content = '''function main() {
    console.log("Hello from stoke!");
}

main();
'''
    main_js.write_text(content, encoding="utf-8")

    # package.json 생성
    package_json = project_root / "package.json"
    if not package_json.exists():
        import json
        pkg = {
            "name": project_root.name,
            "version": "1.0.0",
            "main": "src/main.js",
            "scripts": {},
            "dependencies": {}
        }
        package_json.write_text(json.dumps(pkg, indent=2), encoding="utf-8")