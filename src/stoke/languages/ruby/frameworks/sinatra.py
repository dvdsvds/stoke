"""Sinatra (Ruby) 프로젝트 스캐폴딩."""
import sys
import subprocess
import shutil
from pathlib import Path

from stoke.prompts import resolve_project_dir

def cmd_init_sinatra():
    """stoke init sinatra 명령어."""
    print("Creating Sinatra (Ruby) project\n")

    project_name, project_path = resolve_project_dir("myapp")

    _write_stoke_toml(project_path, project_name)
    _write_gemfile(project_path / "Gemfile")
    (project_path / "src").mkdir(exist_ok=True)
    _write_main_rb(project_path / "src" / "main.rb")

    bundle_exe = shutil.which("bundle")
    if bundle_exe:
        print("Running bundle install...")
        subprocess.run(
            [bundle_exe, "install"],
            cwd=str(project_path),
            capture_output=True,
        )
    else:
        print("Warning: 'bundle' not found. Install Ruby + bundler (gem install bundler)", file=sys.stderr)

    print(f"\nSinatra project created at: {project_path}")
    print()
    print("Next steps:")
    print(f"  cd {project_name}")
    print(f"  stoke build")
    print(f"  stoke run")
    print()
    print("After running, open: http://localhost:4567/")

def _write_stoke_toml(project_path: Path, project_name: str) -> None:
    content = f'''[project]
name = "{project_name}"
version = "0.1.0"
lock_mode = "commit"

[targets.{project_name}]
language = "ruby"
entry = "src/main.rb"
'''
    (project_path / "stoke.toml").write_text(content, encoding="utf-8")

def _write_gemfile(path: Path) -> None:
    content = '''source "https://rubygems.org"

gem "sinatra", "~> 4.0"
'''
    path.write_text(content, encoding="utf-8")

def _write_main_rb(path: Path) -> None:
    content = '''require "sinatra"

set :port, 4567

get "/" do
  "Hello from Sinatra + stoke!"
end

get "/hello/:name" do
  "Hello, #{params[:name]}!"
end
'''
    path.write_text(content, encoding="utf-8")
