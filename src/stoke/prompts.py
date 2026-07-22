"""대화형 입력 프롬프트 공통 헬퍼."""
import sys

def _prompt(question: str, default: str | None = None) -> str:
    """텍스트 입력 받기. 빈 입력이면 default 반환."""
    if default:
        prompt = f"{question} [{default}]: "
    else:
        prompt = f"{question}: "
    answer = input(prompt).strip()
    if not answer and default is not None:
        return default
    return answer

def _prompt_choice(question: str, choices: list[str], default_index: int = 0) -> int:
    """번호로 선택 받기. 1-indexed로 보여주고 0-indexed로 반환."""
    print(f"\n{question}")
    for i, choice in enumerate(choices, start=1):
        marker = " (default)" if (i - 1) == default_index else ""
        print(f"  {i}. {choice}{marker}")
    while True:
        answer = input(f"Select [1-{len(choices)}, default {default_index + 1}]: ").strip()
        if not answer:
            return default_index
        if not answer.isdigit():
            print(f"  Please enter a number between 1 and {len(choices)}")
            continue
        num = int(answer)
        if 1 <= num <= len(choices):
            return num - 1
        print(f"  Please enter a number between 1 and {len(choices)}")

def _prompt_yes_no(question: str, default: bool = True) -> bool:
    """예/아니오 입력."""
    default_str = "Y/n" if default else "y/N"
    while True:
        answer = input(f"{question} [{default_str}]: ").strip().lower()
        if not answer:
            return default
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("Please enter y or n.")