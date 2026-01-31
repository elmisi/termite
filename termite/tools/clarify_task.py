# Third party
from rich.console import Console

# Local
try:
    from termite.dtos import Config
    from termite.shared import call_llm
except ImportError:
    from dtos import Config
    from shared import call_llm


#########
# HELPERS
#########


MAX_QUESTIONS = 10

PROMPT = """You are a requirements analyst for TUI applications.
The user wants to create: "{prompt}"

Ask ONE short, specific yes/no or choice question to clarify a single aspect.

Examples of GOOD questions:
- "Should the list auto-refresh every few seconds?"
- "Do you want keyboard shortcuts to navigate?"
- "Should I include a search/filter feature?"
- "Do you prefer a vertical or horizontal layout?"
- "Should deleted items require confirmation?"

Examples of BAD questions (too generic, don't do this):
- "Could you provide more details on the features and functionalities..."
- "What specific behaviors do you want..."

Rules:
- Ask about ONE thing at a time
- Keep it under 15 words
- Make it easy to answer (yes/no, or 2-3 choices)
- If you have enough information, respond with exactly "DONE"

Context gathered so far:
{context}
"""

console = Console(log_time=False, log_path=False)


def format_context(qa_pairs: list) -> str:
    if not qa_pairs:
        return "(none yet)"

    lines = []
    for q, a in qa_pairs:
        lines.append(f"Q: {q}")
        lines.append(f"A: {a}")
    return "\n".join(lines)


def format_enriched_prompt(original_prompt: str, qa_pairs: list) -> str:
    if not qa_pairs:
        return original_prompt

    lines = [original_prompt, "", "## Clarified Requirements"]
    for q, a in qa_pairs:
        lines.append(f"- Q: {q}")
        lines.append(f"  A: {a}")

    return "\n".join(lines)


######
# MAIN
######


def clarify_task(prompt: str, config: Config) -> str:
    qa_pairs = []

    for i in range(MAX_QUESTIONS):
        context = format_context(qa_pairs)
        system_prompt = PROMPT.format(prompt=prompt, context=context)

        # Force at least one question on first iteration
        if i == 0:
            user_msg = "Ask your first clarifying question. Do NOT respond with DONE yet."
        else:
            user_msg = "What else do you need to know? Respond DONE if you have enough info."

        response = call_llm(
            system=system_prompt,
            messages=[{"role": "user", "content": user_msg}],
            model=config.reasoning_model,
        )
        response = response.strip()

        # Check for DONE (allow after first question)
        if i > 0 and response.upper() == "DONE":
            console.print("[bright_black]No more questions needed.[/bright_black]")
            break

        # Skip if model still says DONE on first iteration (fallback)
        if response.upper() == "DONE":
            console.print("[bright_black]Requirements are clear, proceeding...[/bright_black]")
            break

        console.print(f"[cyan]{response}[/cyan]")
        answer = console.input("[magenta]>[/magenta] ").strip()

        if answer:
            qa_pairs.append((response, answer))

    return format_enriched_prompt(prompt, qa_pairs)
