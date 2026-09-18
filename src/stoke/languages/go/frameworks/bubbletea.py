"""Bubble Tea (Go) 프로젝트 스캐폴딩."""
import sys
import subprocess
import shutil
from pathlib import Path

from stoke.prompts import _prompt, resolve_project_dir, sanitize_go_module_name
from stoke.tool_install import ensure_tool

def cmd_init_bubbletea():
    """stoke init bubbletea 명령어."""
    print("Creating Bubble Tea (Go) project\n")

    project_name, project_path, is_empty = resolve_project_dir("myapp")

    module_name = sanitize_go_module_name(
        _prompt("Go module name (e.g. github.com/user/myapp)", project_name), project_name
    )

    _write_stoke_toml(project_path, project_name)
    _write_main_go(project_path / "main.go")

    go_exe = ensure_tool("go", ("go", "go.exe"), project_path, display_name="Go")
    if go_exe:
        print(f"\nInitializing go.mod (module: {module_name})...")
        result = subprocess.run(
            [go_exe, "mod", "init", module_name],
            cwd=str(project_path),
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print("Warning: go mod init failed:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
        print("Downloading Bubble Tea dependency...")
        result = subprocess.run(
            [go_exe, "get", "github.com/charmbracelet/bubbletea"],
            cwd=str(project_path),
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print("Warning: go get github.com/charmbracelet/bubbletea failed:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
        result = subprocess.run(
            [go_exe, "mod", "tidy"],
            cwd=str(project_path),
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print("Warning: go mod tidy failed:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
    else:
        print("\nWarning: 'go' not found. Run these manually:", file=sys.stderr)
        if not is_empty:
            print(f"  cd {project_name}", file=sys.stderr)
        print(f"  go mod init {module_name}", file=sys.stderr)
        print(f"  go get github.com/charmbracelet/bubbletea", file=sys.stderr)
        print(f"  go mod tidy", file=sys.stderr)

    print(f"\nBubble Tea project created at: {project_path}")
    print()
    print("Next steps:")
    if not is_empty:
        print(f"  cd {project_name}")
    print(f"  stoke build")
    print(f"  stoke run")

def _write_stoke_toml(project_path: Path, project_name: str) -> None:
    content = f'''[project]
name = "{project_name}"
version = "0.1.0"
lock_mode = "commit"

[targets.{project_name}]
language = "go"
'''
    (project_path / "stoke.toml").write_text(content, encoding="utf-8")

def _write_main_go(path: Path) -> None:
    content = '''package main

import (
    "fmt"
    "os"

    tea "github.com/charmbracelet/bubbletea"
)

type model struct {
    choices  []string
    cursor   int
    selected map[int]struct{}
}

func initialModel() model {
    return model{
        choices:  []string{"Build something with stoke", "Ship it", "Get coffee"},
        selected: make(map[int]struct{}),
    }
}

func (m model) Init() tea.Cmd {
    return nil
}

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
    switch msg := msg.(type) {
    case tea.KeyMsg:
        switch msg.String() {
        case "ctrl+c", "q":
            return m, tea.Quit
        case "up", "k":
            if m.cursor > 0 {
                m.cursor--
            }
        case "down", "j":
            if m.cursor < len(m.choices)-1 {
                m.cursor++
            }
        case "enter", " ":
            if _, ok := m.selected[m.cursor]; ok {
                delete(m.selected, m.cursor)
            } else {
                m.selected[m.cursor] = struct{}{}
            }
        }
    }
    return m, nil
}

func (m model) View() string {
    s := "Hello from Bubble Tea + stoke!\\n\\n"

    for i, choice := range m.choices {
        cursor := " "
        if m.cursor == i {
            cursor = ">"
        }
        checked := " "
        if _, ok := m.selected[i]; ok {
            checked = "x"
        }
        s += fmt.Sprintf("%s [%s] %s\\n", cursor, checked, choice)
    }

    s += "\\npress q to quit\\n"
    return s
}

func main() {
    p := tea.NewProgram(initialModel())
    if _, err := p.Run(); err != nil {
        fmt.Println("Error running program:", err)
        os.Exit(1)
    }
}
'''
    path.write_text(content, encoding="utf-8")
