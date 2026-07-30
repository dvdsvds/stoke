"""MSVC 빌드에 필요한 환경변수(vcvarsall) 캡처."""
import os
import subprocess
from pathlib import Path

_env_cache: dict[Path, dict[str, str]] = {}

def get_msvc_env(vcvars_bat: Path) -> dict[str, str]:
    """
    vcvars64.bat을 실행해서 나오는 INCLUDE/LIB/PATH 등을 os.environ 위에 덮어씀.
    cl.exe/link.exe가 표준 헤더(stdio.h 등)와 CRT 라이브러리를 찾으려면 필요함
    (cl.exe는 이 환경변수들 없이는 시스템 헤더조차 못 찾음).
    vcvars_bat 경로 하나당 프로세스 안에서 한 번만 계산하고 캐싱 (~1초 걸림).
    """
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

    # cl.exe/link.exe는 OS 로케일에 따라 진단 메시지를 현지어로 냄 (예: 한국어
    # Windows에서 cp949로 표현 안 되는 문자가 섞여 나와 print()가 그대로 죽는 걸
    # 실제로 확인함). VSLANG=1033(en-US)으로 강제해서 항상 ASCII 영어 메시지만
    # 나오게 함 -- 콘솔 코드페이지에 상관없이 안전하고, CI 로그에서도 더 읽기 쉬움.
    env["VSLANG"] = "1033"

    _env_cache[vcvars_bat] = env
    return env
