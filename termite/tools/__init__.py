try:
    from termite.tools.refine import refine
    from termite.tools.build_tui import build_tui
    from termite.tools.design_tui import design_tui
    from termite.tools.fix_errors import fix_errors
    from termite.tools.clarify_task import clarify_task
except ImportError:
    from tools.refine import refine
    from tools.build_tui import build_tui
    from tools.fix_errors import fix_errors
    from tools.design_tui import design_tui
    from tools.clarify_task import clarify_task
