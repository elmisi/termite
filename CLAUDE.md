# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Termite is a Python CLI that generates terminal user interfaces (TUIs) from natural language prompts using LLMs. It creates Python TUI code, validates it, auto-fixes errors, and optionally refines the output through self-reflection.

## Development Commands

```bash
# Install dependencies
pipenv install

# Install package in editable mode
pip install -e .

# Run the CLI
termite "your prompt here"
termite --library rich "make a process monitor"
termite --refine --refine-iters 2 "show disk usage"
termite --run-tool "saved_tool_name"
```

## Architecture

The application follows a pipeline pattern orchestrated by `termite/termite.py`:

1. **Design** (`tools/design_tui.py`) - LLM generates a design document from user prompt
2. **Build** (`tools/build_tui.py`) - LLM generates Python TUI code from the design
3. **Fix** (`tools/fix_errors.py`) - Iteratively runs the TUI and fixes runtime errors (up to 10 attempts)
4. **Refine** (`tools/refine.py`) - Optional self-reflection loop to improve the code

Key modules:
- `termite/__main__.py` - CLI entry point, argument parsing, script saving/loading
- `shared/call_llm.py` - LLM provider abstraction (OpenAI, Anthropic, Ollama)
- `shared/run_tui.py` - Script execution with syntax validation and pseudo-terminal testing
- `shared/utils/run_pty.py` - Pseudo-terminal execution for capturing stdout/stderr
- `shared/utils/fix_imports.py` - Auto-installs missing packages to venv
- `dtos/Script.py` - Script data class (code, stdout, stderr, reflection)

## LLM Configuration

Requires one of these environment variables:
- `OPENAI_API_KEY` - uses gpt-4o
- `ANTHROPIC_API_KEY` - uses claude-3-5-sonnet-20241022
- `OLLAMA_MODEL` - uses local Ollama

Optional: `OPENAI_BASE_URL` for custom endpoints.

## Saved Scripts

Generated TUIs are saved to `~/.termite/` (or `$XDG_CONFIG_HOME/termite/`). Use `--run-tool` to reload them.

## Code Generation Notes

- LLM responses are parsed for code blocks using XML tags (`<code>`) or markdown fences
- The `Script` class in `dtos/Script.py` holds generated code along with execution output
- Pseudo-terminal execution validates TUIs before presenting to the user
