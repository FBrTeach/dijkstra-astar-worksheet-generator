import os

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')

DIFFICULTY_PRESETS = {
    'Easy':   {'node_count': (5, 6),  'extra_edges': (1, 2), 'weight_range': (1, 10)},
    'Medium': {'node_count': (7, 8),  'extra_edges': (2, 4), 'weight_range': (1, 20)},
    'Hard':   {'node_count': (9, 10), 'extra_edges': (3, 6), 'weight_range': (1, 30)},
}

# 'Escalating' is handled by the app; it maps each question to Easy/Medium/Hard
DIFFICULTY_OPTIONS = ['Easy', 'Medium', 'Hard', 'Escalating']

NODE_LABELS = list('ABCDEFGHIJ')
MAX_RETRIES = 300
ALGORITHM_CHOICES = ['Dijkstra', 'A*', 'Mixed']

FIGURE_SIZE = (7, 5)
FONT_SIZE_NODE = 11
FONT_SIZE_EDGE = 9
FONT_SIZE_HEURISTIC = 8


def escalating_difficulty(index: int, total: int) -> str:
    """Map question index (0-based) to Easy / Medium / Hard on a smooth ramp."""
    if total <= 1:
        return 'Easy'
    t = index / max(total - 1, 1)   # 0.0 → 1.0
    if t < 0.34:
        return 'Easy'
    if t < 0.67:
        return 'Medium'
    return 'Hard'
