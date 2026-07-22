"""TypeScript 프로젝트 초기화 로직."""
from pathlib import Path

def _write_stoke_toml_typescript(
    path: Path,
    project_name: str,
    lock_mode: str,
) -> None:
    """TypeScript 프로젝트용 stoke.toml 쓰기."""
    content = f'''[project]
name = "{project_name}"
version = "0.1.0"
lock_mode = "{lock_mode}"

[targets.{project_name}]
language = "typescript"
entry = "src/main.ts"
'''
    path.write_text(content, encoding="utf-8")

def _write_example_typescript(project_root: Path) -> None:
    """TypeScript 예시 파일 생성."""
    src = project_root / "src"
    src.mkdir(exist_ok=True)
    main_ts = src / "main.ts"
    if main_ts.exists():
        return

    content = '''function main(): void {
    console.log("Hello from stoke!");
}

main();
'''
    main_ts.write_text(content, encoding="utf-8")

    # package.json 생성 (tsx 포함)
    package_json = project_root / "package.json"
    if not package_json.exists():
        import json
        pkg = {
            "name": project_root.name,
            "version": "1.0.0",
            "main": "src/main.ts",
            "scripts": {},
            "devDependencies": {
                "tsx": "^4.0.0",
                "typescript": "^5.0.0",
                "@types/node": "^22.0.0"
            }
        }
        package_json.write_text(json.dumps(pkg, indent=2), encoding="utf-8")

    # tsconfig.json 생성
    tsconfig = project_root / "tsconfig.json"
    if not tsconfig.exists():
        import json
        config = {
            "compilerOptions": {
                "target": "ES2022",
                "module": "ESNext",
                "moduleResolution": "bundler",
                "strict": True,
                "esModuleInterop": True,
                "skipLibCheck": True,
                "outDir": "dist",
                "rootDir": "src"
            },
            "include": ["src/**/*"]
        }
        tsconfig.write_text(json.dumps(config, indent=2), encoding="utf-8")