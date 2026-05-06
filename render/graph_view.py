import math
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from graph.graph import Graph
from config import FIGURE_SIZE, FONT_SIZE_NODE, FONT_SIZE_EDGE, FONT_SIZE_HEURISTIC

NODE_RADIUS_PLAIN = 0.048
NODE_RADIUS_ASTAR = 0.060

# Colours used when a path is highlighted
_PATH_EDGE_COLOUR  = '#e67e22'   # orange
_PATH_NODE_FILL    = '#fef5e7'   # very light orange
_PATH_NODE_EDGE    = '#e67e22'
_FADE_EDGE_COLOUR  = '#bbbbbb'   # greyed-out non-path edges
_FADE_NODE_EDGE    = '#aaaaaa'   # greyed-out non-path node borders

# Start / goal node colours (always applied, take priority over path highlighting)
_START_FILL = '#eafaf1'
_START_EDGE = '#27ae60'   # green
_END_FILL   = '#fdedec'
_END_EDGE   = '#c0392b'   # red


def draw_graph_on_axes(ax, graph: Graph, highlight_path=None):
    """
    Draw the graph onto an existing Axes (coordinate space [0,1]²).

    highlight_path — optional list of node labels forming the shortest path.
                     When supplied, path edges are drawn in orange and faded
                     for non-path elements, making the route immediately clear.
    """
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.axis('off')

    pos     = graph.positions
    is_astar = graph.heuristics is not None
    node_r   = NODE_RADIUS_ASTAR if is_astar else NODE_RADIUS_PLAIN

    # Pre-compute path sets
    path_node_set = set()
    path_edge_set = set()
    if highlight_path and len(highlight_path) >= 2:
        path_node_set = set(highlight_path)
        for i in range(len(highlight_path) - 1):
            u, v = highlight_path[i], highlight_path[i + 1]
            path_edge_set.add((u, v))
            path_edge_set.add((v, u))
    highlighting = bool(path_edge_set)

    # ---- Edges -------------------------------------------------------
    # Draw non-path edges first (lower zorder), path edges on top
    for u, v, w in graph.edges:
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        on_path = (u, v) in path_edge_set

        colour = _PATH_EDGE_COLOUR if on_path else (
                 _FADE_EDGE_COLOUR if highlighting else '#333333')
        lw     = 2.8 if on_path else 1.5
        z      = 2   if on_path else 1

        ax.plot([x1, x2], [y1, y2], color=colour, linewidth=lw, zorder=z,
                solid_capstyle='round')

        # Weight label — always readable, slightly faded when not on path
        edge_len = math.hypot(x2 - x1, y2 - y1)
        ux, uy   = ((x2 - x1) / edge_len, (y2 - y1) / edge_len) \
                   if edge_len > 1e-6 else (1.0, 0.0)
        mx, my   = _safe_label_pos((x1 + x2) / 2, (y1 + y2) / 2,
                                   ux, uy, edge_len, pos, node_r)

        label_colour = _PATH_EDGE_COLOUR if on_path else (
                       '#888888' if highlighting else '#222222')
        ec           = _PATH_EDGE_COLOUR if on_path else '#888888'

        ax.text(mx, my, str(w),
                ha='center', va='center',
                fontsize=FONT_SIZE_EDGE, fontweight='bold',
                color=label_colour,
                bbox=dict(boxstyle='round,pad=0.18',
                          fc='white', ec=ec, linewidth=0.7),
                zorder=3)

    # ---- Nodes -------------------------------------------------------
    for node in graph.nodes:
        x, y     = pos[node]
        on_path  = node in path_node_set
        is_start = (node == graph.start)
        is_end   = (node == graph.goal)

        # Start/end colours always take priority over path highlighting.
        if is_start:
            face, edge_c, lw = _START_FILL, _START_EDGE, 2.5
        elif is_end:
            face, edge_c, lw = _END_FILL, _END_EDGE, 2.5
        elif highlighting:
            face  = _PATH_NODE_FILL if on_path else 'white'
            edge_c = _PATH_NODE_EDGE if on_path else _FADE_NODE_EDGE
            lw     = 2.5 if on_path else 1.5
        else:
            face, edge_c, lw = 'white', '#333333', 2.0

        circle = plt.Circle((x, y), node_r,
                             color=face, ec=edge_c,
                             linewidth=lw, zorder=4)
        ax.add_patch(circle)

        txt_colour = (_START_EDGE if is_start else
                      _END_EDGE   if is_end   else
                      _PATH_NODE_EDGE if (highlighting and on_path) else
                      '#aaaaaa'   if (highlighting and not on_path) else 'black')

        if is_astar:
            ax.text(x, y + node_r * 0.32, node,
                    ha='center', va='center',
                    fontsize=FONT_SIZE_NODE - 1, fontweight='bold',
                    color=txt_colour, zorder=5)
            ax.text(x, y - node_r * 0.35,
                    str(graph.heuristics[node]),
                    ha='center', va='center',
                    fontsize=FONT_SIZE_HEURISTIC, fontstyle='italic',
                    color=txt_colour, zorder=5)
        else:
            ax.text(x, y, node,
                    ha='center', va='center',
                    fontsize=FONT_SIZE_NODE, fontweight='bold',
                    color=txt_colour, zorder=5)


def build_figure(graph: Graph, question_num: int, total: int,
                 seed: int, difficulty: str,
                 highlight_path=None) -> plt.Figure:
    """Standalone figure for embedding in the GUI canvas."""
    fig, ax = plt.subplots(figsize=FIGURE_SIZE)
    draw_graph_on_axes(ax, graph, highlight_path=highlight_path)

    algo_label = ("A*  (node label / heuristic inside each circle)"
                  if graph.heuristics else "Dijkstra's")
    title = (f"Question {question_num} of {total}  —  {algo_label}  —  "
             f"Difficulty: {difficulty}  —  Seed: {seed}\n"
             f"Find the shortest path from  {graph.start}  to  {graph.goal}")
    ax.set_title(title, fontsize=9, pad=8)

    fig.tight_layout(pad=0.4)
    return fig


# ---------------------------------------------------------------------------
# Label-position helper (shared with layout.py logic, duplicated here
# so graph_view has no import dependency on layout)
# ---------------------------------------------------------------------------

_LABEL_CLEAR = 0.075


def _safe_label_pos(mx, my, edge_dx, edge_dy, edge_len, node_positions, node_r):
    perp_x, perp_y = -edge_dy, edge_dx
    half_len = edge_len / 2
    if half_len < node_r + 0.01:
        shift = math.sqrt(max(0.0, (_LABEL_CLEAR ** 2) - (half_len ** 2))) + 0.01
        mx += perp_x * shift
        my += perp_y * shift
    for _ in range(6):
        for node, (nx, ny) in node_positions.items():
            d = math.hypot(mx - nx, my - ny)
            if d < _LABEL_CLEAR and d > 1e-6:
                proj = (mx - nx) * perp_x + (my - ny) * perp_y
                direction = 1 if proj >= 0 else -1
                needed = _LABEL_CLEAR - d + 0.005
                mx += direction * perp_x * needed
                my += direction * perp_y * needed
    return mx, my
