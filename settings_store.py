"""
Lightweight persistence for the GUI's input settings.
Reads/writes a JSON file next to main.py so settings survive restarts.
"""
import json
import os

_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     '.last_settings.json')

_DEFAULTS = {
    'algorithm':      'Dijkstra',
    'difficulty':     'Medium',
    'num_questions':  5,
    'seed':           '42',
    'output_folder':  '',        # empty → replaced by OUTPUT_DIR at runtime
    'student_name':   '',
    'student_class':  '',
    'student_date':   '',
    'show_working':      False,
    'include_title_page': True,
}


def load() -> dict:
    """Return saved settings merged over defaults (missing keys get defaults)."""
    if os.path.exists(_PATH):
        try:
            with open(_PATH, 'r', encoding='utf-8') as f:
                saved = json.load(f)
            return {**_DEFAULTS, **saved}
        except Exception:
            pass
    return dict(_DEFAULTS)


def save(settings: dict) -> None:
    """Persist settings dict to disk (silently ignores write errors)."""
    try:
        with open(_PATH, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2)
    except Exception:
        pass
