"""
Builds the answer-table widget inside a tkinter Frame.
Used by question_panel.py — returns (table_frame, footer_frame).
"""
import tkinter as tk
from tkinter import font as tkfont
from graph.graph import Question

_COL_DIJKSTRA = ['Node', 'Distance travelled', 'Previous node']
_COL_ASTAR    = ['Node', 'Distance travelled', 'Heuristic',
                 'Distance + Heuristic', 'Previous node']

_COL_WIDTHS = {
    'Node':                   6,
    'Distance travelled':    18,
    'Heuristic':             12,
    'Distance + Heuristic':  22,
    'Previous node':         15,
}


def build_table_frame(parent, question: Question, revealed: bool,
                      show_working: bool = False):
    """
    Returns (table_frame, footer_frame).

    When show_working=True and revealed=True (Dijkstra only), the table shows
    every relaxation event in chronological order; superseded rows are struck through.
    Otherwise the standard alphabetical summary table is rendered.
    """
    use_working = (show_working and revealed
                   and question.algorithm == 'Dijkstra'
                   and question.working_steps)

    if use_working:
        frame   = _build_working_table(parent, question)
    else:
        frame   = _build_summary_table(parent, question, revealed)

    footer = _build_footer(parent, question, revealed)
    return frame, footer


# ---------------------------------------------------------------------------

def _build_summary_table(parent, question: Question, revealed: bool):
    cols   = _COL_ASTAR if question.algorithm == 'A*' else _COL_DIJKSTRA
    n_nodes = len(question.graph.nodes)
    step_map = {s.node: s for s in question.steps}

    frame = tk.Frame(parent, bd=1, relief='flat')

    # Header
    for c, col in enumerate(cols):
        tk.Label(frame, text=col, font=('Arial', 9, 'bold'),
                 relief='ridge', bd=1, padx=4, pady=3,
                 width=_COL_WIDTHS[col], bg='#dde3ea',
                 anchor='center').grid(row=0, column=c, sticky='nsew')

    # Data rows — exactly n_nodes rows, all blank when not revealed
    for r in range(n_nodes):
        node_label = question.graph.nodes[r] if r < n_nodes else ''
        step = step_map.get(node_label) if revealed else None

        for c, col in enumerate(cols):
            val = _cell_value(step, col) if (revealed and step) else ''
            tk.Label(frame, text=val,
                     font=('Arial', 9), relief='ridge', bd=1,
                     padx=4, pady=3, width=_COL_WIDTHS[col],
                     bg='white', anchor='center').grid(
                row=r + 1, column=c, sticky='nsew')

    return frame


def _build_working_table(parent, question: Question):
    """Dijkstra working table: chronological relaxations, superseded rows struck through."""
    cols = _COL_DIJKSTRA
    font_normal = ('Arial', 9)
    font_struck = tkfont.Font(family='Arial', size=9, overstrike=True)

    frame = tk.Frame(parent, bd=1, relief='flat')

    # Header
    for c, col in enumerate(cols):
        tk.Label(frame, text=col, font=('Arial', 9, 'bold'),
                 relief='ridge', bd=1, padx=4, pady=3,
                 width=_COL_WIDTHS[col], bg='#dde3ea',
                 anchor='center').grid(row=0, column=c, sticky='nsew')

    for r, ws in enumerate(question.working_steps):
        bg   = 'white' if ws.is_final else '#f5f5f5'
        fg   = '#333333' if ws.is_final else '#aaaaaa'
        font = font_normal if ws.is_final else font_struck
        vals = [ws.node, str(ws.distance),
                ws.previous if ws.previous else 'N/A']
        for c, val in enumerate(vals):
            tk.Label(frame, text=val, font=font, fg=fg,
                     relief='ridge', bd=1, padx=4, pady=2,
                     width=_COL_WIDTHS[cols[c]], bg=bg,
                     anchor='center').grid(row=r + 1, column=c, sticky='nsew')

    return frame


def _build_footer(parent, question: Question, revealed: bool):
    footer = tk.Frame(parent)
    if revealed:
        path_str = ' → '.join(question.final_path)
        dist_str = str(question.final_distance)
    else:
        path_str = '.' * 50
        dist_str = '.' * 20

    tk.Label(footer, text='Final path:', font=('Arial', 9, 'bold'),
             anchor='w').grid(row=0, column=0, sticky='w', padx=(0, 4))
    tk.Label(footer, text=path_str, font=('Arial', 9),
             anchor='w').grid(row=0, column=1, sticky='w')
    tk.Label(footer, text='Distance:', font=('Arial', 9, 'bold'),
             anchor='w').grid(row=1, column=0, sticky='w', padx=(0, 4))
    tk.Label(footer, text=dist_str, font=('Arial', 9),
             anchor='w').grid(row=1, column=1, sticky='w')

    if revealed and question.comparison_note:
        tk.Label(footer, text=question.comparison_note,
                 font=('Arial', 8, 'italic'), fg='#555555',
                 anchor='w', wraplength=550).grid(
            row=2, column=0, columnspan=2, sticky='w', pady=(4, 0))

    return footer


# ---------------------------------------------------------------------------

def _cell_value(step, col: str) -> str:
    if col == 'Node':                  return step.node
    if col == 'Distance travelled':    return str(step.distance)
    if col == 'Heuristic':             return str(step.heuristic) if step.heuristic is not None else ''
    if col == 'Distance + Heuristic':  return str(step.f_score)   if step.f_score   is not None else ''
    if col == 'Previous node':         return step.previous if step.previous else 'N/A'
    return ''
