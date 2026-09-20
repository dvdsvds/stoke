# 캐시 파일 손상 시 KeyError + lock.py 리턴 타입 오류

- 날짜: 2026-09-18
- 심각도: low
- 상태: 수정됨

## 1. `cache.py`: 손상된 캐시 항목에서 KeyError

`load_cache()`가 `(json.JSONDecodeError, OSError)`는 최상위 `json.load` 주변에서만 잡고, 그 안쪽 `stat_data["mtime"]`/`stat_data["size"]` 인덱싱은 별도 보호가 없었음. 손으로 편집했거나 쓰다 만 `.stoke/cache.json`에 필드 빠진 항목이 있으면 docstring이 약속하는 "손상되면 빈 캐시로"가 안 지켜지고 `KeyError`가 그대로 터짐.

**수정**: 파싱 루프 전체를 `try/except (KeyError, TypeError, AttributeError)`로 감싸서 실패 시 `BuildCache()` 반환.

## 2. `lock.py`: `save_lock()` 리턴 타입 어노테이션이 실제와 다름

`-> Path`라고 선언되어 있는데 실제로는 항상 `(path, bool)` 튜플을 반환함. 현재 호출부 3곳은 다 올바르게 언패킹하고 있어서 런타임 버그는 아니었지만, 다음에 이 함수를 쓰는 사람이나 타입 체커를 혼란시킬 수 있는 지뢰였음.

**수정**: `-> tuple[Path, bool]`로 정정, docstring도 반환값 설명 추가.

## 변경 파일

- `src/stoke/cache.py`
- `src/stoke/lock.py`
