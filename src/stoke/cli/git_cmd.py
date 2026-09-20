"""stoke git -- add/commit/push를 위한 대화형 메뉴 (stoke init처럼 questionary 기반)."""
import sys
from pathlib import Path

from stoke import git_setup
from stoke.prompts import _prompt, _prompt_checkbox, _prompt_choice

def _do_add(cwd: Path) -> None:
    changed = git_setup.get_changed_files(cwd)
    if not changed:
        print("No changes to add.")
        return
    selected = _prompt_checkbox("Select files to add (space to toggle, enter to confirm)", changed)
    if not selected:
        print("Nothing selected.")
        return
    if git_setup.git_add(cwd, selected):
        print(f"Added {len(selected)} file(s).")
    else:
        print("Error: 'git add' failed.", file=sys.stderr)

def _do_commit(cwd: Path) -> None:
    staged = git_setup.get_staged_files(cwd)
    if not staged:
        print("Nothing staged -- use 'Add files' first.")
        return
    message = _prompt("Commit message")
    if not message:
        print("Empty message, cancelled.")
        return
    ok, result = git_setup.git_commit(cwd, message)
    if ok:
        print(f"\n----- {result} -----")
        print("Committed.")
    else:
        print(f"Error: commit failed: {result}", file=sys.stderr)

def _do_push(cwd: Path) -> None:
    current = git_setup.current_branch(cwd) or "main"
    branches = git_setup.list_branches(cwd)
    choices = branches + ["+ New branch name..."]
    default_index = branches.index(current) if current in branches else 0
    selected = choices[_prompt_choice("Push to which branch?", choices, default_index=default_index)]

    branch = _prompt("New branch name", default=current) if selected == "+ New branch name..." else selected

    print(f"Pushing to origin/{branch}...")
    ok, message = git_setup.git_push(cwd, branch)
    if ok:
        print(f"Pushed to origin/{branch}.")
    else:
        print(f"Error: push failed: {message}", file=sys.stderr)

def cmd_git() -> None:
    """stoke git -- add/commit/push 메뉴, Exit 고를 때까지 반복."""
    cwd = Path.cwd()
    repo_root = git_setup.find_parent_git_repo(cwd)
    if repo_root is None:
        print(
            "Error: not inside a git repository here.\n"
            "  Run 'git init' (or 'stoke init' and say yes to the git prompt) first.",
            file=sys.stderr,
        )
        sys.exit(1)

    actions = {"Add files": _do_add, "Commit": _do_commit, "Push": _do_push}
    choices = list(actions) + ["Exit"]

    while True:
        branch = git_setup.current_branch(cwd) or "(no branch)"
        changed = len(git_setup.get_changed_files(cwd))
        print(f"\nOn branch '{branch}', {changed} file(s) changed.")

        choice = choices[_prompt_choice("What would you like to do?", choices, default_index=0)]
        if choice == "Exit":
            return
        actions[choice](cwd)
