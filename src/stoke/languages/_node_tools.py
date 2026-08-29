"""JS/TS 어댑터 공용 Node 툴 탐색 믹스인"""
import shutil
import sys

class NodeToolsMixin:
    def _find_local_node_dir(self):
        """프로젝트의 .stoke/toolchains/nodejs-*/ 에서 stoke install로 받은 Node.js 폴더 찾기.
        압축 풀면 안에 node-vX.Y.Z-<os>-<arch>/ 폴더가 한 겹 더 있음."""
        toolchains = self.project_root / ".stoke" / "toolchains"
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

    def _find_node(self) -> str:
        """프로젝트 로컬 설치(.stoke/toolchains)를 PATH보다 우선."""
        local_dir = self._find_local_node_dir()
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

    def _find_npm(self) -> str:
        local_dir = self._find_local_node_dir()
        if local_dir is not None:
            npm_name = "npm.cmd" if sys.platform == "win32" else "npm"
            npm_path = local_dir / npm_name if sys.platform == "win32" else local_dir / "bin" / npm_name
            if npm_path.is_file():
                return str(npm_path)

        npm = shutil.which("npm")
        if npm is None:
            raise RuntimeError("npm not found in PATH.\n  Install Node.js first.")
        return npm