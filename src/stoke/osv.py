"""OSV.dev 배치 취약점 조회 (python/java는 별도 스캐너 설치 없이 lock 파일 기준으로 직접 조회)."""
import json
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

_BATCH_URL = "https://api.osv.dev/v1/querybatch"
_VULN_URL = "https://api.osv.dev/v1/vulns/{}"
_MAX_WORKERS = 8

class OsvVuln:
    def __init__(self, id: str, summary: str | None):
        self.id = id
        self.summary = summary

def query_batch(ecosystem: str, packages: dict[str, str], timeout: int = 20) -> dict[str, list[OsvVuln]]:
    """{name: version} -> {name: [OsvVuln, ...]} (취약점 없는 패키지는 키에서 빠짐)."""
    if not packages:
        return {}

    names = list(packages.keys())
    body = json.dumps({
        "queries": [
            {"package": {"name": name, "ecosystem": ecosystem}, "version": packages[name]}
            for name in names
        ]
    }).encode("utf-8")

    req = urllib.request.Request(
        _BATCH_URL, data=body, method="POST",
        headers={"Content-Type": "application/json", "User-Agent": "stoke-audit"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = json.loads(response.read())
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error querying OSV.dev: {getattr(e, 'reason', e)}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error querying OSV.dev: {e}")

    results = data.get("results", [])
    found: dict[str, list[OsvVuln]] = {}
    ids_by_name: dict[str, list[str]] = {}
    for name, result in zip(names, results):
        ids = [v["id"] for v in result.get("vulns", []) if "id" in v]
        if ids:
            ids_by_name[name] = ids

    if not ids_by_name:
        return {}

    # querybatch는 id/modified만 주므로, summary는 vuln별로 따로 조회
    all_ids = {vid for ids in ids_by_name.values() for vid in ids}
    summaries = _fetch_summaries(all_ids, timeout)

    for name, ids in ids_by_name.items():
        found[name] = [OsvVuln(id=vid, summary=summaries.get(vid)) for vid in ids]
    return found

def _fetch_one_summary(vid: str, timeout: int) -> str | None:
    try:
        req = urllib.request.Request(
            _VULN_URL.format(vid), headers={"User-Agent": "stoke-audit"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            vuln_data = json.loads(response.read())
        return vuln_data.get("summary")
    except Exception:
        return None

def _fetch_summaries(ids: set[str], timeout: int) -> dict[str, str | None]:
    ids = list(ids)
    with ThreadPoolExecutor(max_workers=min(_MAX_WORKERS, len(ids))) as pool:
        results = pool.map(lambda vid: _fetch_one_summary(vid, timeout), ids)
        return dict(zip(ids, results))
