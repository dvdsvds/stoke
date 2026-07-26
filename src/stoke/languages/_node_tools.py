"""JS/TS 어댑터 공용 Node 툴 탐색 믹스인"""
import shutil

class NodeToolsMixin:
    def _find_node(self) -> str:
        node = shutil.which("node")
        if node is None:
            raise RuntimeError(
                "node not found in PATH.\n"
                "  Install with: stoke install --language=nodejs --version=latest"
            )
        return node

    def _find_npm(self) -> str:
        npm = shutil.which("npm")
        if npm is None:
            raise RuntimeError("npm not found in PATH.\n  Install Node.js first.")
        return npm