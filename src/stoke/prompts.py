"""대화형 입력 프롬프트 공통 헬퍼.

가능하면 questionary로 화살표 키 기반 TUI를 보여주고, stdin/stdout이
실제 터미널이 아니거나(파이프/리다이렉트, CI) questionary를 쓸 수 없으면
기존의 번호 입력 방식으로 자동 폴백한다.
"""
import sys
from pathlib import Path

try:
    import questionary
    from questionary import Style
    from prompt_toolkit import Application
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.layout.containers import HSplit, VSplit, Window
    from prompt_toolkit.layout.layout import Layout
    from prompt_toolkit.styles import Style as PTStyle
    from prompt_toolkit.widgets import Label, TextArea
    from prompt_toolkit.widgets.base import Border as _PTBorder
    from questionary.prompts.common import InquirerControl as _InquirerControl

    # questionary의 선택 목록은 현재 커서가 있는 항목에 "[SetCursorPosition]"
    # 토큰을 심어서, 매 프레임마다 터미널의 실제(네이티브) 커서를 그 위치로
    # 강제 이동시킨다. 이 네이티브 커서가 일부 터미널에서 해당 줄 전체를
    # 흰 배경 블록으로 그려버리고, 커서를 옮겨도 이전 위치에 남는 버그를
    # 일으켜서 -- 토큰 자체를 걸러내 네이티브 커서가 표시되지 않게 만든다.
    _original_get_choice_tokens = _InquirerControl._get_choice_tokens

    def _get_choice_tokens_no_cursor(self):
        return [
            token
            for token in _original_get_choice_tokens(self)
            if token[0] != "[SetCursorPosition]"
        ]

    _InquirerControl._get_choice_tokens = _get_choice_tokens_no_cursor

    # questionary는 select()의 default 항목을 커서 위치와 무관하게 영구히
    # "class:selected"로 표시하는데, prompt_toolkit 기본 스타일이
    # selected = reverse라서 이게 흰 배경(리버스 비디오)으로 렌더링되고
    # 커서를 옮겨도 default 항목에 계속 남아있는 문제가 있었다.
    # checkbox의 실제 체크 상태(choice.checked)만 selected로 남기고,
    # select()의 "이게 default였다" 표시는 없앤다 -- 커서 위치 표시는
    # highlighted 스타일 하나로만 하면 충분하다.
    def _is_selected_checked_only(self, choice):
        return choice.checked

    _InquirerControl._is_selected = _is_selected_checked_only

    # 기본 각진 모서리(┌┐└┘) 대신 둥근 모서리(╭╮╰╯) 사용 -- gum 스타일
    _PTBorder.TOP_LEFT = "╭"
    _PTBorder.TOP_RIGHT = "╮"
    _PTBorder.BOTTOM_LEFT = "╰"
    _PTBorder.BOTTOM_RIGHT = "╯"

    # 커서(highlighted)와 checkbox 체크 항목(selected)은 로고 색(주황) 배경으로
    # 표시한다. noreverse를 명시하는 이유: prompt_toolkit 기본 스타일이
    # highlighted/selected에 reverse를 깔아두는 경우가 있어, 커스텀 배경색을
    # 줘도 리버스 비디오가 우선 적용되며 흰 배경으로 보이는 문제가 있었다.
    _QUESTIONARY_STYLE = Style([
        ("qmark", "fg:#5f87ff bold"),
        ("question", "bold"),
        ("highlighted", "bg:#ff8710 fg:#000000 bold noreverse"),
        ("selected", "bg:#ff8710 fg:#000000 bold noreverse"),
    ])
    _POINTER = None
    # 텍스트 입력용 테두리 박스 스타일 (로고 오렌지색과 통일)
    _BOX_STYLE = PTStyle.from_dict({
        "frame.border": "fg:#ff8710",
        "frame.label": "fg:#ff8710 bold",
    })
    _HAS_QUESTIONARY = True
except ImportError:
    _HAS_QUESTIONARY = False

def _border_fill(char: str, width: int | None = None) -> Window:
    return Window(width=width, height=1, char=char, style="class:frame.border")

def _boxed_container(text_area: TextArea, title: str, width: int) -> HSplit:
    """제목은 윗 테두리에, 입력은 그 아랫줄에. 입력 커서 시작 위치를 제목의
    첫 글자(P) 바로 밑에 맞춘다 -- 윗줄 "╭─ P..." 만큼 왼쪽에 패딩을 둠."""
    top = VSplit(
        [
            _border_fill(_PTBorder.TOP_LEFT, width=1),
            _border_fill(_PTBorder.HORIZONTAL, width=1),
            Label(f" {title} ", style="class:frame.label", dont_extend_width=True),
            _border_fill(_PTBorder.HORIZONTAL),
            _border_fill(_PTBorder.TOP_RIGHT, width=1),
        ],
        height=1,
    )
    middle = VSplit(
        [
            _border_fill(_PTBorder.VERTICAL, width=1),
            _border_fill(" ", width=2),
            text_area,
            _border_fill(_PTBorder.VERTICAL, width=1),
        ],
        padding=0,
    )
    bottom = VSplit(
        [
            _border_fill(_PTBorder.BOTTOM_LEFT, width=1),
            _border_fill(_PTBorder.HORIZONTAL),
            _border_fill(_PTBorder.BOTTOM_RIGHT, width=1),
        ],
        height=1,
    )
    return HSplit([top, middle, bottom], width=width, style="class:frame")

def _prompt_boxed(question: str, default: str = "") -> str | None:
    """gum 스타일 테두리 박스 안에 텍스트 입력. Ctrl-C면 None 반환."""
    text_area = TextArea(text=default, multiline=False)
    text_area.buffer.cursor_position = len(default)
    kb = KeyBindings()

    @kb.add("enter")
    def _submit(event) -> None:
        event.app.exit(result=text_area.text)

    @kb.add("c-c")
    def _cancel(event) -> None:
        event.app.exit(result=None)

    box_width = max(len(question) + 6, len(default) + 10, 35)
    box = _boxed_container(text_area, question, box_width)
    left_pad = Window(width=1)  # 박스를 왼쪽 끝에서 한 칸 띄움
    app = Application(
        layout=Layout(VSplit([left_pad, box])),
        key_bindings=kb,
        style=_BOX_STYLE,
        full_screen=False,
    )
    return app.run()

def _use_tui() -> bool:
    """화살표 키 TUI를 쓸 수 있는 환경인지: questionary 설치 + 실제 tty."""
    return _HAS_QUESTIONARY and sys.stdin.isatty() and sys.stdout.isatty()

def _abort_on_cancel(answer):
    """questionary는 Ctrl-C/ESC 시 None을 반환한다."""
    if answer is None:
        print("Aborted.")
        sys.exit(1)
    return answer

def _prompt(question: str, default: str | None = None) -> str:
    """텍스트 입력 받기. 빈 입력이면 default 반환."""
    if _use_tui():
        answer = _abort_on_cancel(_prompt_boxed(question, default or "")).strip()
        if not answer and default is not None:
            return default
        return answer
    if default:
        prompt = f"{question} [{default}]: "
    else:
        prompt = f"{question}: "
    answer = input(prompt).strip()
    if not answer and default is not None:
        return default
    return answer

def resolve_project_name(default_name: str = "myapp") -> tuple[str, bool]:
    """프로젝트 이름 프롬프트. 반환: (project_name, cwd가 비어있었는지)"""
    cwd = Path.cwd()
    is_empty = not any(cwd.iterdir())
    project_name = _prompt("Project name", cwd.name if is_empty else default_name)
    return project_name, is_empty

def resolve_project_dir(default_name: str = "myapp") -> tuple[str, Path, bool]:
    """이름 프롬프트 + 디렉토리 생성. 반환: (project_name, project_path, is_empty)

    is_empty가 True면 project_path는 cwd 자체이고 하위 디렉토리가 생성되지 않았으므로,
    호출부의 "다음 단계" 안내에서 `cd {project_name}`을 출력하면 안 됨.
    """
    project_name, is_empty = resolve_project_name(default_name)
    cwd = Path.cwd()
    if is_empty:
        return project_name, cwd, True
    project_path = cwd / project_name
    if project_path.exists():
        print(f"Error: directory '{project_name}' already exists", file=sys.stderr)
        sys.exit(1)
    project_path.mkdir()
    return project_name, project_path, False

def _prompt_choice(question: str, choices: list[str], default_index: int = 0) -> int:
    """선택지 중 하나를 고르게 하고 0-indexed로 반환.

    TUI 모드에서는 화살표 키로 이동하는 목록으로, 폴백 모드에서는
    번호를 타이핑하는 기존 방식으로 보여준다.
    """
    if _use_tui():
        # 일부 터미널에서 네이티브 텍스트 커서(깜빡이는 블록)가 첫 항목에
        # 고정되어 보이는 문제를 막기 위해 선택 중엔 커서를 숨긴다.
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()
        try:
            answer = _abort_on_cancel(
                questionary.select(
                    question,
                    choices=choices,
                    default=choices[default_index],
                    style=_QUESTIONARY_STYLE,
                    pointer=_POINTER,
                ).ask()
            )
        finally:
            sys.stdout.write("\033[?25h")
            sys.stdout.flush()
        return choices.index(answer)
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
    if _use_tui():
        return _abort_on_cancel(
            questionary.confirm(question, default=default, style=_QUESTIONARY_STYLE).ask()
        )
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
