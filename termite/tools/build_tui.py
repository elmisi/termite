# Standard library
from typing import Optional

# Third party
from rich.progress import Progress

# Local
try:
    from termite.dtos import Script, Config
    from termite.shared import call_llm, MAX_TOKENS
except ImportError:
    from dtos import Script, Config
    from shared import call_llm, MAX_TOKENS


#########
# HELPERS
#########


PROGRESS_LIMIT = MAX_TOKENS // 15
PROMPT = """You are an expert Python programmer tasked with building a terminal user interface (TUI).
You will be given a design document that describes the TUI and its requirements. Your job is to implement the TUI using the {library} library.

CRITICAL RULES:
- Use ONLY the {library} library. Do NOT use any other TUI libraries.
- Use ONLY classes and functions that ACTUALLY EXIST in {library}. Do NOT invent or guess widget names.
- Do NOT use try/except blocks. All exceptions must be raised.
- Ensure the TUI takes up the full terminal width/height.

{library_hints}

Output your response in this format:

<thoughts>
Your step-by-step implementation plan goes here...
</thoughts>

<code>
# Your complete Python code here
</code>

Double-check that every import and class you use actually exists in {library}."""

LIBRARY_HINTS = {
    "rich": """RICH LIBRARY - Available components:
- Console, Table, Panel, Layout, Live
- Progress, Spinner, Status
- Text, Markdown, Syntax
- Prompt.ask() for input
Use Live() context manager for dynamic updates.""",

    "textual": """TEXTUAL LIBRARY - Available widgets:
- App, Screen, Widget, Static, Label, Button
- DataTable, ListView, Tree, Input, TextArea
- Header, Footer, Container, Horizontal, Vertical
- Use compose() method to yield widgets
- Use CSS for styling via CSS property or .tcss files""",

    "urwid": """URWID LIBRARY - Available widgets:
- Text, Edit, Button, CheckBox, RadioButton
- Pile, Columns, Frame, Filler, Padding
- ListBox, SimpleFocusListWalker
- MainLoop for event handling
- Use palette for colors""",

    "curses": """CURSES LIBRARY:
- Use stdscr.addstr(), stdscr.getch()
- curses.wrapper() for initialization
- curses.newwin() for windows
- Handle KEY_UP, KEY_DOWN, etc."""
}


def get_library_hints(library: str) -> str:
    return LIBRARY_HINTS.get(library, "")


def parse_code(output: str) -> str:
    def _parse_tags() -> Optional[str]:
        chunks = output.split("<code>")

        if len(chunks) == 1:
            return None

        code = chunks[1].split("</code>")[0].strip()
        return code

    def _parse_delimiters() -> Optional[str]:
        chunks = output.split("```")

        if len(chunks) == 1:
            return None

        code = "```".join(chunks[1:-1]).strip()
        if code.split("\n")[0].lower().startswith("python"):
            code = "\n".join(code.split("\n")[1:])

        return code

    if code := _parse_tags():
        return code

    if code := _parse_delimiters():
        return code

    return output


######
# MAIN
######


def build_tui(design: str, p_bar: Progress, config: Config) -> Script:
    task = p_bar.add_task("build", total=PROGRESS_LIMIT)

    library_hints = get_library_hints(config.library)
    output = call_llm(
        system=PROMPT.format(library=config.library, library_hints=library_hints),
        messages=[{"role": "user", "content": design}],
        stream=True,
    )
    code = ""
    for token in output:
        code += token
        p_bar.update(task, advance=1)
    code = parse_code(code)
    script = Script(code=code)

    p_bar.update(task, completed=PROGRESS_LIMIT)
    return script
