# Third party
from rich.progress import Progress

# Local

try:
    from termite.dtos import Script, Config
    from termite.shared import run_tui, call_llm, MAX_TOKENS
except ImportError:
    from dtos import Script, Config
    from shared import run_tui, call_llm, MAX_TOKENS


#########
# HELPERS
#########


PROMPT = """You are an expert Python programmer tasked with fixing a terminal user interface (TUI) implementation.
Your goal is to analyze, debug, and rewrite a broken Python script to make the TUI work without errors.

CRITICAL RULES:
1. Use ONLY the {library} library. Do NOT use any other TUI libraries.
2. Use ONLY classes and functions that ACTUALLY EXIST in {library}. Do NOT invent widgets or methods.
3. Do NOT use try/except blocks. All exceptions must ALWAYS be raised.
4. Ensure the TUI adheres to the original design document.

COMMON MISTAKES TO AVOID:
- Importing non-existent classes (e.g. ScrolledList, HeaderBar don't exist in textual)
- Using wrong method names or signatures
- Missing required parameters in constructors

Before fixing, verify that every import and class you use actually exists in {library}.

Respond with ONLY the complete, fixed Python script. No explanations, no markdown formatting."""


def parse_code(output: str) -> str:
    chunks = output.split("```")

    if len(chunks) == 1:
        return output

    code = "```".join(chunks[1:-1]).strip()
    if code.split("\n")[0].lower().startswith("python"):
        code = "\n".join(code.split("\n")[1:])

    return code


######
# MAIN
######


def fix_errors(
    script: Script, design: str, incr_p_bar: callable, config: Config
) -> Script:
    num_retries = 0
    curr_script = script
    previous_errors = []

    while num_retries < config.fix_iters:
        run_tui(curr_script)

        if not curr_script.stderr:
            return curr_script

        # Track error history to detect loops
        current_error = curr_script.stderr
        previous_errors.append(current_error)

        # Build error context
        error_context = f"<error>\n{current_error}\n</error>"
        if len(previous_errors) > 1:
            error_context += f"\n\nThis is attempt {num_retries + 1}. Previous errors were similar - make sure you're using REAL classes/methods from {config.library}."

        messages = [
            {"role": "user", "content": design},
            {"role": "assistant", "content": curr_script.code},
            {
                "role": "user",
                "content": f"{error_context}\n\nFix the error above. Use ONLY real, existing classes from {config.library}.",
            },
        ]
        output = call_llm(
            system=PROMPT.format(library=config.library),
            messages=messages,
            stream=True,
            prediction={"type": "content", "content": curr_script.code},
        )
        code = ""
        for token in output:
            code += token
            incr_p_bar()
        code = parse_code(code)
        curr_script = Script(code=code)

        num_retries += 1

    return curr_script


# TODO: Use self-consistency
