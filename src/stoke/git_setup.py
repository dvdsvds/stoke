"""stoke init 마지막에 물어보는 git 저장소 초기화 + GitHub 원격 생성 (전부 최선을 다해 보고, 실패해도 조용히 안내만)."""
import platform
import shutil
import subprocess
from pathlib import Path

def find_parent_git_repo(start: Path) -> Path | None:
    """start부터 상위로 올라가며 .git 디렉토리를 찾음 (중첩 저장소 방지용)."""
    current = start.resolve()
    while True:
        if (current / ".git").exists():
            return current
        if current.parent == current:
            return None
        current = current.parent

def is_git_installed() -> bool:
    return shutil.which("git") is not None

def install_git_globally() -> bool:
    """OS별 패키지 매니저로 git을 전역 설치 시도. 시스템 전체에 영향 주는 유일한 stoke 설치 동작 --
    다른 언어 툴체인처럼 프로젝트 로컬(.stoke/toolchains/)로는 넣을 수 없음(모든 프로젝트/git 자체가 PATH에서 찾아야 함).
    """
    system = platform.system()

    if system == "Windows":
        if shutil.which("winget") is None:
            print("winget not found. Install Git manually from: https://git-scm.com/download/win")
            return False
        print("Installing Git via winget...")
        result = subprocess.run([
            "winget", "install", "--id", "Git.Git", "-e", "--source", "winget",
            "--accept-package-agreements", "--accept-source-agreements",
        ])
        return result.returncode == 0

    if system == "Darwin":
        if shutil.which("brew") is not None:
            print("Installing Git via Homebrew...")
            result = subprocess.run(["brew", "install", "git"])
            return result.returncode == 0
        print(
            "Homebrew not found. Run 'xcode-select --install' to get Git from Apple's "
            "Command Line Tools, or install Homebrew first: https://brew.sh"
        )
        return False

    if system == "Linux":
        managers = [
            (("apt-get",), ["sudo", "apt-get", "update"], ["sudo", "apt-get", "install", "-y", "git"]),
            (("dnf",), None, ["sudo", "dnf", "install", "-y", "git"]),
            (("pacman",), None, ["sudo", "pacman", "-Sy", "--noconfirm", "git"]),
            (("zypper",), None, ["sudo", "zypper", "install", "-y", "git"]),
            (("apk",), None, ["sudo", "apk", "add", "git"]),
        ]
        for (exe,), update_cmd, install_cmd in managers:
            if shutil.which(exe) is None:
                continue
            print(f"Installing Git via {exe}...")
            if update_cmd:
                subprocess.run(update_cmd)
            result = subprocess.run(install_cmd)
            return result.returncode == 0
        print("No supported package manager found (tried apt-get/dnf/pacman/zypper/apk). Install Git manually.")
        return False

    print(f"Don't know how to install Git on '{system}'. Install it manually: https://git-scm.com/downloads")
    return False

def git_init(project_dir: Path) -> bool:
    result = subprocess.run(["git", "init"], cwd=str(project_dir), capture_output=True, text=True)
    return result.returncode == 0

def git_commit_all(project_dir: Path, message: str) -> bool:
    """git add -A + commit. lock_mode(commit/local)에 상관없이 항상 동작 -- .gitignore가 이미
    lock_mode="local"의 lock 파일 등을 제외해두므로, 뭘 커밋에 넣을지 여기서 따로 안 가려도 됨."""
    add = subprocess.run(["git", "add", "-A"], cwd=str(project_dir), capture_output=True, text=True)
    if add.returncode != 0:
        return False
    commit = subprocess.run(["git", "commit", "-m", message], cwd=str(project_dir), capture_output=True, text=True)
    return commit.returncode == 0

# ============================================================
# stoke git (add/commit/push 대화형 메뉴)
# ============================================================

def get_changed_files(project_dir: Path) -> list[str]:
    """git status --porcelain 결과에서 파일 경로만 추출 (untracked/modified/staged 전부 포함)."""
    result = subprocess.run(
        ["git", "status", "--porcelain"], cwd=str(project_dir), capture_output=True, text=True,
    )
    if result.returncode != 0:
        return []
    files = []
    for line in result.stdout.splitlines():
        path = line[3:]
        if " -> " in path:  # rename: "old -> new"
            path = path.split(" -> ", 1)[1]
        files.append(path.strip('"'))
    return files

def get_staged_files(project_dir: Path) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"], cwd=str(project_dir), capture_output=True, text=True,
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]

def git_add(project_dir: Path, files: list[str]) -> bool:
    result = subprocess.run(["git", "add", "--"] + files, cwd=str(project_dir), capture_output=True, text=True)
    return result.returncode == 0

def git_commit(project_dir: Path, message: str) -> tuple[bool, str]:
    """반환: (성공 여부, 성공하면 짧은 해시 / 실패하면 에러 메시지)."""
    result = subprocess.run(
        ["git", "commit", "-m", message], cwd=str(project_dir), capture_output=True, text=True,
    )
    if result.returncode != 0:
        return False, (result.stderr.strip() or result.stdout.strip())
    hash_result = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"], cwd=str(project_dir), capture_output=True, text=True,
    )
    return True, hash_result.stdout.strip()

def current_branch(project_dir: Path) -> str:
    result = subprocess.run(
        ["git", "branch", "--show-current"], cwd=str(project_dir), capture_output=True, text=True,
    )
    return result.stdout.strip()

def list_branches(project_dir: Path) -> list[str]:
    result = subprocess.run(
        ["git", "branch", "--format=%(refname:short)"], cwd=str(project_dir), capture_output=True, text=True,
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]

def git_push(project_dir: Path, branch: str) -> tuple[bool, str]:
    """HEAD를 origin/<branch>로 push (원격에 그 브랜치가 없으면 git이 알아서 새로 만들어서 올림)."""
    result = subprocess.run(
        ["git", "push", "-u", "origin", f"HEAD:{branch}"], cwd=str(project_dir), capture_output=True, text=True,
    )
    return result.returncode == 0, (result.stderr.strip() or result.stdout.strip())

# ============================================================
# GitHub 원격 저장소 (gh CLI 필요)
# ============================================================

def is_gh_available() -> bool:
    """gh CLI가 설치돼 있고 로그인까지 돼 있는지."""
    if shutil.which("gh") is None:
        return False
    result = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True)
    return result.returncode == 0

def list_github_owners() -> list[str]:
    """[내 계정, 소속 조직들...] -- 실패하면 빈 리스트."""
    owners = []
    me = subprocess.run(["gh", "api", "user", "-q", ".login"], capture_output=True, text=True)
    if me.returncode == 0 and me.stdout.strip():
        owners.append(me.stdout.strip())
    orgs = subprocess.run(["gh", "api", "user/orgs", "-q", ".[].login"], capture_output=True, text=True)
    if orgs.returncode == 0:
        owners.extend(line.strip() for line in orgs.stdout.splitlines() if line.strip())
    return owners

def github_repo_exists(owner: str, name: str) -> bool:
    result = subprocess.run(["gh", "repo", "view", f"{owner}/{name}"], capture_output=True, text=True)
    return result.returncode == 0

def create_github_remote(project_dir: Path, owner: str, name: str, private: bool) -> str | None:
    """빈 GitHub 저장소 생성(커밋/푸시 없이) + origin으로 연결. 성공하면 URL 반환, 실패하면 None."""
    visibility = "--private" if private else "--public"
    result = subprocess.run(
        ["gh", "repo", "create", f"{owner}/{name}", visibility],
        cwd=str(project_dir), capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"Warning: failed to create GitHub repo: {result.stderr.strip()}")
        return None

    url = f"https://github.com/{owner}/{name}.git"
    remote_result = subprocess.run(
        ["git", "remote", "add", "origin", url], cwd=str(project_dir), capture_output=True, text=True,
    )
    if remote_result.returncode != 0:
        print(f"Warning: repo created but failed to add git remote: {remote_result.stderr.strip()}")
        return None
    return url
