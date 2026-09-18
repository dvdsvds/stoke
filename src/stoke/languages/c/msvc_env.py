"""MSVC 빌드에 필요한 환경변수(vcvarsall) 캡처."""
import os
import subprocess
from pathlib import Path

_env_cache: dict[Path, dict[str, str]] = {}

def get_msvc_env(vcvars_bat: Path) -> dict[str, str]:
    """vcvars64.bat 실행 결과(INCLUDE/LIB/PATH 등)를 캡처 (경로당 한 번만 계산 후 캐싱)."""
    if vcvars_bat in _env_cache:
        return _env_cache[vcvars_bat]

    result = subprocess.run(
        f'"{vcvars_bat}" >nul && set',
        shell=True,
        capture_output=True,
        text=True,
        errors="replace",
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Failed to set up MSVC environment via {vcvars_bat}:\n{result.stderr.strip()}"
        )

    env = dict(os.environ)
    for line in result.stdout.splitlines():
        key, sep, value = line.partition("=")
        if sep:
            env[key] = value

    # 로케일별 진단 메시지가 콘솔 코드페이지로 인코딩 안 돼 깨지는 걸 방지 (en-US 강제)
    env["VSLANG"] = "1033"

    _env_cache[vcvars_bat] = env
    return env
