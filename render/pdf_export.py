"""
PDF worksheet generator.
Each question occupies one A4 page: graph on top, blank answer table below.
'include_answers=True' appends a filled answer page immediately after each question.
'include_title_page=True' prepends a title page with student info and question list.
"""
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from graph.graph import Question
from render.graph_view import draw_graph_on_axes

A4_W, A4_H = 8.27, 11.69

_COL_DIJKSTRA = ['Node', 'Distance travelled', 'Previous node']
_COL_ASTAR    = ['Node', 'Distance travelled', 'Heuristic',
                 'Distance + Heuristic', 'Previous node']

_WIDTHS_DIJKSTRA = [0.12, 0.44, 0.44]
_WIDTHS_ASTAR    = [0.10, 0.20, 0.16, 0.26, 0.28]

_WIDTHS_WORKING  = [0.12, 0.44, 0.44]


def export_pdf(questions: list, filepath: str, include_answers: bool = False,
               student_info: dict = None, show_working: bool = False,
               include_title_page: bool = True):
    info = student_info or {}
    with PdfPages(filepath) as pdf:
        if include_title_page:
            fig_title = _build_title_page(questions, info)
            pdf.savefig(fig_title, bbox_inches='tight')
            plt.close(fig_title)

        for i, q in enumerate(questions):
            fig = _build_page(q, i + 1, len(questions),
                              revealed=False, show_working=False)
            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)

            if include_answers:
                fig_ans = _build_page(q, i + 1, len(questions),
                                      revealed=True, show_working=show_working)
                pdf.savefig(fig_ans, bbox_inches='tight')
                plt.close(fig_ans)


# ---------------------------------------------------------------------------

def _build_title_page(questions: list, info: dict) -> plt.Figure:
    fig = plt.figure(figsize=(A4_W, A4_H))
    ax = fig.add_axes([0.12, 0.05, 0.76, 0.90])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # Title block
    ax.text(0.5, 0.94, 'Graph Algorithm Worksheet',
            ha='center', va='top', fontsize=24, fontweight='bold')
    ax.text(0.5, 0.87, 'OCR A Level Computer Science  —  H446',
            ha='center', va='top', fontsize=11, color='#555555')

    ax.axhline(0.83, color='#333333', linewidth=1.5, xmin=0, xmax=1)

    # Student info fields
    y = 0.76
    fields = [
        ('Name',  'student_name'),
        ('Class', 'student_class'),
        ('Date',  'student_date'),
    ]
    for label, key in fields:
        ax.text(0.0, y, f'{label}:', fontsize=14, fontweight='bold', va='top')
        val = info.get(key, '').strip()
        if val:
            ax.text(0.22, y, val, fontsize=14, va='top')
        else:
            ax.plot([0.22, 0.98], [y - 0.028, y - 0.028],
                    color='#555555', linewidth=0.9)
        y -= 0.09

    ax.axhline(y - 0.01, color='#aaaaaa', linewidth=0.8, xmin=0, xmax=1)
    y -= 0.06

    # Question list
    ax.text(0.0, y, 'Questions in this set:', fontsize=11,
            fontweight='bold', va='top', color='#333333')
    y -= 0.045

    # Column headers
    for x, header, w in [(0.02, '#', 0.06), (0.10, 'Algorithm', 0.25),
                          (0.38, 'Difficulty', 0.25), (0.65, 'Seed', 0.15),
                          (0.82, 'Start → Goal', 0.18)]:
        ax.text(x, y, header, fontsize=8.5, fontweight='bold',
                va='top', color='#555555')
    y -= 0.008
    ax.axhline(y, color='#aaaaaa', linewidth=0.5, xmin=0, xmax=1)
    y -= 0.030

    for i, q in enumerate(questions):
        if y < 0.04:
            break
        bg = '#f7f7f7' if i % 2 == 0 else 'white'
        rect = mpatches.FancyBboxPatch(
            (0.0, y - 0.025), 1.0, 0.034,
            boxstyle='square,pad=0',
            facecolor=bg, edgecolor='none',
            transform=ax.transData, clip_on=False)
        ax.add_patch(rect)

        diff  = getattr(q, 'difficulty', '')
        start = q.graph.start
        goal  = q.graph.goal
        for x, text in [(0.02, str(i + 1)),
                        (0.10, q.algorithm),
                        (0.38, diff),
                        (0.65, str(q.seed)),
                        (0.82, f'{start} → {goal}')]:
            ax.text(x, y, text, fontsize=9, va='top', color='#222222')
        y -= 0.034

    return fig


# ---------------------------------------------------------------------------

def _build_page(question: Question, num: int, total: int,
                revealed: bool, show_working: bool) -> plt.Figure:
    fig = plt.figure(figsize=(A4_W, A4_H))

    # Header
    ax_hdr = fig.add_axes([0.05, 0.925, 0.90, 0.055])
    ax_hdr.axis('off')
    algo   = question.algorithm
    diff   = getattr(question, 'difficulty', '')
    status = 'ANSWER KEY' if revealed else 'Worksheet'
    ax_hdr.text(0.0, 0.85,
                f"Question {num} of {total}  —  {algo} Algorithm  —  "
                f"Difficulty: {diff}  —  Seed: {question.seed}  —  {status}",
                fontsize=9, fontweight='bold', va='top')
    ax_hdr.text(0.0, 0.20,
                f"Find the shortest path from "
                f"{question.graph.start} to {question.graph.goal}.",
                fontsize=9, va='top')

    # Graph — highlight path on answer-key pages
    ax_graph = fig.add_axes([0.05, 0.52, 0.90, 0.40])
    highlight = question.final_path if revealed else None
    draw_graph_on_axes(ax_graph, question.graph, highlight_path=highlight)
    if question.graph.heuristics:
        ax_graph.set_title(
            'Heuristic values shown in italics inside each node.',
            fontsize=8, pad=4, color='#555555')

    # Table
    use_working = (show_working and revealed
                   and question.algorithm == 'Dijkstra'
                   and question.working_steps)
    ax_tbl = fig.add_axes([0.05, 0.15, 0.90, 0.36])
    if use_working:
        _draw_working_table(ax_tbl, question)
    else:
        _draw_table(ax_tbl, question, revealed)

    # Footer
    ax_ftr = fig.add_axes([0.05, 0.03, 0.90, 0.11])
    _draw_footer(ax_ftr, question, revealed)

    return fig


# ---------------------------------------------------------------------------

def _draw_table(ax, question: Question, revealed: bool):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    cols   = _COL_ASTAR    if question.algorithm == 'A*' else _COL_DIJKSTRA
    widths = _WIDTHS_ASTAR if question.algorithm == 'A*' else _WIDTHS_DIJKSTRA

    n_nodes      = len(question.graph.nodes)
    step_map     = {s.node: s for s in question.steps}
    n_rows_total = n_nodes + 1
    row_h        = 0.95 / n_rows_total

    for row_idx in range(n_rows_total):
        y_top = 1.0 - row_idx * row_h
        y_bot = y_top - row_h
        x     = 0.0
        is_header = (row_idx == 0)

        data_idx  = row_idx - 1
        node_name = (question.graph.nodes[data_idx]
                     if 0 <= data_idx < n_nodes else None)
        step      = step_map.get(node_name) if (revealed and node_name) else None

        for col, cw in zip(cols, widths):
            fc = '#d8dfe8' if is_header else 'white'
            rect = mpatches.FancyBboxPatch(
                (x + 0.002, y_bot + 0.001), cw - 0.004, row_h - 0.002,
                boxstyle='square,pad=0',
                facecolor=fc, edgecolor='#555555', linewidth=0.6,
                transform=ax.transData, clip_on=False)
            ax.add_patch(rect)

            if is_header:
                text, fs, fw = col, 7.5, 'bold'
            elif step:
                text, fs, fw = _cell_value(step, col), 9, 'normal'
            else:
                text, fs, fw = '', 9, 'normal'

            ax.text(x + cw / 2, (y_top + y_bot) / 2, text,
                    ha='center', va='center',
                    fontsize=fs, fontweight=fw, clip_on=False)
            x += cw


def _draw_working_table(ax, question: Question):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    cols   = _COL_DIJKSTRA
    widths = _WIDTHS_WORKING
    steps  = question.working_steps

    n_rows_total = len(steps) + 1
    row_h = 0.95 / n_rows_total
    fs    = max(6.0, min(9.0, row_h * 95))

    for row_idx in range(n_rows_total):
        y_top = 1.0 - row_idx * row_h
        y_bot = y_top - row_h
        x     = 0.0
        is_header = (row_idx == 0)
        ws = steps[row_idx - 1] if not is_header else None

        for col, cw in zip(cols, widths):
            fc = '#d8dfe8' if is_header else ('white' if (ws and ws.is_final) else '#f5f5f5')
            rect = mpatches.FancyBboxPatch(
                (x + 0.002, y_bot + 0.001), cw - 0.004, row_h - 0.002,
                boxstyle='square,pad=0',
                facecolor=fc, edgecolor='#555555', linewidth=0.5,
                transform=ax.transData, clip_on=False)
            ax.add_patch(rect)

            if is_header:
                text, fw, colour = col, 'bold', 'black'
            else:
                text   = _working_cell(ws, col)
                fw     = 'normal'
                colour = '#333333' if ws.is_final else '#aaaaaa'

            cy = (y_top + y_bot) / 2
            ax.text(x + cw / 2, cy, text,
                    ha='center', va='center',
                    fontsize=fs if not is_header else 7.5,
                    fontweight=fw, color=colour, clip_on=False)

            if ws and not ws.is_final and text:
                ax.plot([x + 0.005, x + cw - 0.005], [cy, cy],
                        color='#aaaaaa', linewidth=0.8, clip_on=False)
            x += cw


def _working_cell(ws, col: str) -> str:
    if col == 'Node':               return ws.node
    if col == 'Distance travelled': return str(ws.distance)
    if col == 'Previous node':      return ws.previous if ws.previous else 'N/A'
    return ''


def _cell_value(step, col: str) -> str:
    if col == 'Node':                  return step.node
    if col == 'Distance travelled':    return str(step.distance)
    if col == 'Heuristic':             return str(step.heuristic) if step.heuristic is not None else ''
    if col == 'Distance + Heuristic':  return str(step.f_score)   if step.f_score   is not None else ''
    if col == 'Previous node':         return step.previous if step.previous else 'N/A'
    return ''


# ---------------------------------------------------------------------------

def _draw_footer(ax, question: Question, revealed: bool):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    dot = '.' * 70

    path_val = '  →  '.join(question.final_path) if revealed else dot
    dist_val = str(question.final_distance)       if revealed else dot[:25]

    ax.text(0.00, 0.95, 'Final path:', fontsize=9, fontweight='bold', va='top')
    ax.text(0.15, 0.95, path_val,      fontsize=9, va='top')
    ax.text(0.00, 0.60, 'Distance:',   fontsize=9, fontweight='bold', va='top')
    ax.text(0.15, 0.60, dist_val,      fontsize=9, va='top')
    ax.text(0.98, 0.95, '[7]', fontsize=9, fontweight='bold',
            ha='right', va='top', color='#333333')

    if revealed and question.comparison_note:
        ax.text(0.00, 0.22, question.comparison_note,
                fontsize=7.5, fontstyle='italic', va='top', color='#555555')
