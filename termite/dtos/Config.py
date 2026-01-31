# Standard library
import os
from dataclasses import dataclass, field


def _default_model() -> str:
    return os.getenv("OLLAMA_MODEL", "")


@dataclass
class Config:
    library: str = "urwid"
    should_refine: bool = False
    refine_iters: int = 1
    fix_iters: int = 10
    # Model for clarification and design phases
    reasoning_model: str = field(default_factory=_default_model)
    # Model for coding and debugging phases
    coding_model: str = field(default_factory=_default_model)
