"""JS/TS 어댑터 공용 Node 툴 탐색. 모듈 레벨 함수라 어댑터 인스턴스 없이도(stoke add/remove) 재사용 가능."""
import shutil
import sys
from pathlib import Path

def find_local_node_dir(project_root: Path):
    """.stoke/toolchains/nodejs-*/ 에서 stoke install로 받은 Node.js 폴더 찾기."""
    toolchains = project_root / ".stoke" / "toolchains"
    if not toolchains.is_dir():
        return None
    for d in sorted(toolchains.iterdir(), reverse=True):
        if not d.is_dir() or not d.name.startswith("nodejs-"):
            continue
        nested = [c for c in d.iterdir() if c.is_dir() and c.name.startswith("node-")]
        if nested:
            return nested[0]
        if (d / ("node.exe" if sys.platform == "win32" else "bin/node")).exists():
            return d
    return None

def find_node(project_root: Path) -> str:
    """프로젝트 로컬 설치(.stoke/toolchains)를 PATH보다 우선."""
    local_dir = find_local_node_dir(project_root)
    if local_dir is not None:
        exe = local_dir / "node.exe" if sys.platform == "win32" else local_dir / "bin" / "node"
        if exe.is_file():
            return str(exe)

    node = shutil.which("node")
    if node is None:
        raise RuntimeError(
            "node not found in PATH.\n"
            "  Install with: stoke install --language=nodejs --version=latest"
        )
    return node

def find_npm(project_root: Path) -> str:
    """프로젝트 로컬 설치(.stoke/toolchains)를 PATH보다 우선."""
    local_dir = find_local_node_dir(project_root)
    if local_dir is not None:
        npm_name = "npm.cmd" if sys.platform == "win32" else "npm"
        npm_path = local_dir / npm_name if sys.platform == "win32" else local_dir / "bin" / npm_name
        if npm_path.is_file():
            return str(npm_path)

    npm = shutil.which("npm")
    if npm is None:
        raise RuntimeError("npm not found in PATH.\n  Install Node.js first.")
    return npm

class NodeToolsMixin:
    def _find_local_node_dir(self):
        return find_local_node_dir(self.project_root)

    def _find_node(self) -> str:
        return find_node(self.project_root)

    def _find_npm(self) -> str:
        return find_npm(self.project_root)

    def _run_npm_script(self, script: str) -> int:
        """package.json의 scripts.<script>를 npm run <script>로 실행 (dev-server 기반 프레임워크의 `stoke run`)."""
        import subprocess

        package_json = self.project_root / "package.json"
        if not package_json.exists():
            raise RuntimeError("No package.json found, nothing to run.")

        npm_exe = self._find_npm()
        cmd = [npm_exe, "run", script]
        print(f"Running: npm run {script}\n")
        try:
            result = subprocess.run(cmd, cwd=str(self.project_root), shell=(sys.platform == "win32"))
            return result.returncode
        except KeyboardInterrupt:
            return 130

    def _run_npm_test(self, verbose: bool = False) -> int:
        """package.json의 "scripts.test"를 npm test로 실행. JS/TS 어댑터 공용."""
        import json
        import subprocess

        package_json = self.project_root / "package.json"
        if not package_json.exists():
            raise RuntimeError("No package.json found, nothing to test.")

        try:
            scripts = json.loads(package_json.read_text(encoding="utf-8")).get("scripts", {})
        except (OSError, ValueError):
            scripts = {}

        if "test" not in scripts:
            raise RuntimeError(
                'No "test" script found in package.json.\n'
                '  Add one under "scripts", e.g. "test": "vitest run" or "test": "jest".'
            )

        npm_exe = self._find_npm()
        cmd = [npm_exe, "test"]
        print("Running: npm test\n")
        try:
            result = subprocess.run(cmd, cwd=str(self.project_root), shell=(sys.platform == "win32"))
            return result.returncode
        except KeyboardInterrupt:
            return 130