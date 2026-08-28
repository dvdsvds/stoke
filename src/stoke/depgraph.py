"""타겟 간 depends_on 의존성 그래프: 검증 + 위상 정렬."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from stoke.config import Target


def validate_depends_on(targets: dict[str, "Target"]) -> None:
    """알 수 없는 타겟 참조, 자기참조, 순환 의존성을 검사. 문제 있으면 ValueError."""
    for name, target in targets.items():
        for dep in target.depends_on:
            if dep == name:
                raise ValueError(f"Target '{name}' cannot depend on itself")
            if dep not in targets:
                raise ValueError(f"Target '{name}' depends on unknown target '{dep}'")
    _check_cycles(targets)


def _check_cycles(targets: dict[str, "Target"]) -> None:
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {name: WHITE for name in targets}
    path: list[str] = []

    def visit(name: str) -> None:
        color[name] = GRAY
        path.append(name)
        for dep in targets[name].depends_on:
            if color[dep] == GRAY:
                cycle = path[path.index(dep):] + [dep]
                raise ValueError(f"Circular dependency: {' -> '.join(cycle)}")
            if color[dep] == WHITE:
                visit(dep)
        path.pop()
        color[name] = BLACK

    for name in targets:
        if color[name] == WHITE:
            visit(name)


def closure(targets: dict[str, "Target"], name: str) -> list[str]:
    """name과 그 의존성 전체(전이적)를 빌드 순서대로 반환 (name이 마지막)."""
    order: list[str] = []
    seen: set[str] = set()

    def visit(n: str) -> None:
        if n in seen:
            return
        seen.add(n)
        for dep in targets[n].depends_on:
            visit(dep)
        order.append(n)

    visit(name)
    return order


def build_waves(targets: dict[str, "Target"], names: list[str]) -> list[list[str]]:
    """names에 속한 타겟들을 의존성 순서를 지키는, 병렬 실행 가능한 배치들로 나눔."""
    remaining = set(names)
    done: set[str] = set()
    waves: list[list[str]] = []
    while remaining:
        wave = [
            n for n in remaining
            if all(d in done or d not in remaining for d in targets[n].depends_on)
        ]
        if not wave:
            raise ValueError("Circular dependency detected among targets")
        for n in wave:
            remaining.discard(n)
        done.update(wave)
        waves.append(sorted(wave))
    return waves
