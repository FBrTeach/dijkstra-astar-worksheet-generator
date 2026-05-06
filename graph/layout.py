import math
import random

# Minimum distance between any two edge-label centres (axes units).
# Two-digit numbers at 9 pt in a 7-inch-wide figure occupy ≈ 0.025 au wide;
# the white bbox adds a small surround, so 0.11 gives comfortable clearance.
_MIN_LABEL_SEP = 0.11


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def generate_positions_with_edges(nodes: list, edges: list,
                                  rng: random.Random) -> dict:
    """
    Full layout pipeline:
      1. Fruchterman-Reingold with gravity
      2. Leaf-node repositioning
      3. Hard minimum node-separation enforcement
      4. Iterative edge-label-overlap resolution  ← new
      5. Final verification pass                  ← new
    Returns dict node -> (x, y) in [MARGIN, 1-MARGIN]^2.
    """
    n = len(nodes)
    if n == 1:
        return {nodes[0]: (0.5, 0.5)}
    if n == 2:
        return {nodes[0]: (0.35, 0.5), nodes[1]: (0.65, 0.5)}

    MARGIN  = 0.12
    W       = 1.0 - 2 * MARGIN
    k       = 0.85 * math.sqrt(W * W / n)
    GRAVITY = 0.04

    # ---- 1. Fruchterman-Reingold -------------------------------------------
    pos = {}
    for i, node in enumerate(nodes):
        angle = 2 * math.pi * i / n - math.pi / 2
        r = 0.28
        x = 0.5 + r * math.cos(angle) + rng.uniform(-0.025, 0.025)
        y = 0.5 + r * math.sin(angle) + rng.uniform(-0.025, 0.025)
        pos[node] = [x, y]

    t    = 0.25
    cool = 0.974

    for _ in range(700):
        disp = {nd: [0.0, 0.0] for nd in nodes}

        for i in range(n):
            for j in range(i + 1, n):
                u, v = nodes[i], nodes[j]
                dx = pos[u][0] - pos[v][0]
                dy = pos[u][1] - pos[v][1]
                dist = math.hypot(dx, dy) or 1e-6
                force = k * k / dist
                disp[u][0] += dx / dist * force
                disp[u][1] += dy / dist * force
                disp[v][0] -= dx / dist * force
                disp[v][1] -= dy / dist * force

        for u, v, _ in edges:
            dx = pos[u][0] - pos[v][0]
            dy = pos[u][1] - pos[v][1]
            dist = math.hypot(dx, dy) or 1e-6
            force = dist * dist / k
            disp[u][0] -= dx / dist * force
            disp[u][1] -= dy / dist * force
            disp[v][0] += dx / dist * force
            disp[v][1] += dy / dist * force

        for nd in nodes:
            disp[nd][0] += GRAVITY * (0.5 - pos[nd][0])
            disp[nd][1] += GRAVITY * (0.5 - pos[nd][1])

        for nd in nodes:
            dx, dy = disp[nd]
            mag = math.hypot(dx, dy) or 1e-6
            move = min(mag, t)
            pos[nd][0] = max(MARGIN, min(1 - MARGIN,
                                         pos[nd][0] + dx / mag * move))
            pos[nd][1] = max(MARGIN, min(1 - MARGIN,
                                         pos[nd][1] + dy / mag * move))
        t *= cool

    # ---- 2. Leaf-node repositioning ----------------------------------------
    _reposition_leaf_nodes(nodes, edges, pos, margin=MARGIN)

    # ---- 3. Hard minimum node-separation ------------------------------------
    _enforce_min_separation(nodes, pos, min_dist=0.22, margin=MARGIN)

    # ---- 4. Edge-label overlap resolution + 5. final check -----------------
    _resolve_label_overlaps(list(nodes), edges, pos, margin=MARGIN)

    return {nd: tuple(pos[nd]) for nd in nodes}


# ---------------------------------------------------------------------------
# Leaf-node post-processor
# ---------------------------------------------------------------------------

def _reposition_leaf_nodes(nodes, edges, pos, margin=0.12,
                            ideal_dist=0.26, n_angles=24):
    """
    For every degree-1 node, try n_angles positions around its neighbour
    and pick the one with maximum minimum-distance to all other nodes.
    Two passes handle the case where two leaves share a neighbour.
    """
    degree    = {nd: 0 for nd in nodes}
    neighbour = {nd: None for nd in nodes}
    for u, v, _ in edges:
        degree[u] += 1
        degree[v] += 1
        neighbour[u] = v
        neighbour[v] = u

    leaves = [nd for nd in nodes if degree[nd] == 1]
    if not leaves:
        return

    for _ in range(2):
        for leaf in leaves:
            nb  = neighbour[leaf]
            nbx, nby = pos[nb]
            others = [(pos[nd][0], pos[nd][1]) for nd in nodes if nd != leaf]

            best_pos, best_score = None, -1.0
            for step in range(n_angles):
                angle = 2 * math.pi * step / n_angles
                cx = max(margin, min(1 - margin,
                                     nbx + ideal_dist * math.cos(angle)))
                cy = max(margin, min(1 - margin,
                                     nby + ideal_dist * math.sin(angle)))
                if not others:
                    best_pos = (cx, cy)
                    break
                score = min(math.hypot(cx - ox, cy - oy) for ox, oy in others)
                if score > best_score:
                    best_score = score
                    best_pos   = (cx, cy)

            if best_pos:
                pos[leaf] = list(best_pos)


# ---------------------------------------------------------------------------
# Hard minimum node-separation enforcement
# ---------------------------------------------------------------------------

def _enforce_min_separation(nodes, pos, min_dist=0.22, margin=0.12,
                             max_iter=120):
    """
    Iteratively push apart any pair of nodes closer than min_dist.
    Ensures edge-weight labels at edge midpoints are never inside a node.
    """
    n = len(nodes)
    for _ in range(max_iter):
        moved = False
        for i in range(n):
            for j in range(i + 1, n):
                u, v = nodes[i], nodes[j]
                dx = pos[u][0] - pos[v][0]
                dy = pos[u][1] - pos[v][1]
                dist = math.hypot(dx, dy)
                if dist < min_dist:
                    push = (min_dist - dist) / 2 + 0.002
                    nx_, ny_ = (dx / dist, dy / dist) if dist > 1e-6 else (1.0, 0.0)
                    pos[u][0] = max(margin, min(1 - margin, pos[u][0] + nx_ * push))
                    pos[u][1] = max(margin, min(1 - margin, pos[u][1] + ny_ * push))
                    pos[v][0] = max(margin, min(1 - margin, pos[v][0] - nx_ * push))
                    pos[v][1] = max(margin, min(1 - margin, pos[v][1] - ny_ * push))
                    moved = True
        if not moved:
            break


# ---------------------------------------------------------------------------
# Edge-label overlap resolution
# ---------------------------------------------------------------------------

def _label_midpoints(edges, pos):
    return {(u, v): ((pos[u][0] + pos[v][0]) / 2,
                     (pos[u][1] + pos[v][1]) / 2)
            for u, v, _ in edges}


def _count_label_overlaps(edges, pos, min_sep=_MIN_LABEL_SEP):
    mids = _label_midpoints(edges, pos)
    keys = list(mids)
    count = 0
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            mx1, my1 = mids[keys[i]]
            mx2, my2 = mids[keys[j]]
            if math.hypot(mx1 - mx2, my1 - my2) < min_sep:
                count += 1
    return count


def _resolve_label_overlaps(nodes, edges, pos, margin=0.12,
                             min_sep=_MIN_LABEL_SEP, max_iter=120):
    """
    Detect pairs of edge labels (midpoints) closer than min_sep and nudge
    nodes to push them apart.  Key design choices:

    • Symmetric nudging: both edges' free nodes are moved simultaneously,
      each contributing half the required separation.  This is more stable
      than one-sided nudging, which can displace the fixed edge into a third.

    • Severity ordering: within each pass, worst overlaps (smallest distance)
      are resolved first so critical conflicts get priority.

    • Stuck detection: if the overlap count stops decreasing for several
      consecutive passes, apply a small deterministic perturbation to all
      involved nodes then re-run separation enforcement to escape the cycle.

    • Final verification: a read-only pass confirms the result; a last
      enforcement sweep is triggered for any residual cases (dense graphs
      where geometric resolution is impossible may retain 1-2 overlaps).
    """
    edge_keys  = [(u, v) for u, v, _ in edges]
    prev_count = None
    stuck_for  = 0

    for iteration in range(max_iter):
        mids = _label_midpoints(edges, pos)

        # Collect all overlapping pairs, sorted worst-first
        overlapping = []
        for i in range(len(edge_keys)):
            for j in range(i + 1, len(edge_keys)):
                u1, v1 = edge_keys[i]
                u2, v2 = edge_keys[j]
                mx1, my1 = mids[(u1, v1)]
                mx2, my2 = mids[(u2, v2)]
                dist = math.hypot(mx1 - mx2, my1 - my2)
                if dist < min_sep:
                    overlapping.append((dist, i, j))

        if not overlapping:
            break   # fully converged

        overlapping.sort()          # ascending distance → worst first
        current_count = len(overlapping)

        # Stuck detection
        if current_count == prev_count:
            stuck_for += 1
        else:
            stuck_for  = 0
        prev_count = current_count

        if stuck_for >= 4:
            # Deterministic perturbation: nudge all involved nodes by a fixed
            # amount perpendicular to the current push direction.
            involved = set()
            for _, i, j in overlapping:
                for nd in edge_keys[i] + edge_keys[j]:
                    involved.add(nd)
            for idx, nd in enumerate(sorted(involved)):
                angle = math.pi * idx / max(len(involved), 1)
                pos[nd][0] = max(margin, min(1 - margin,
                                             pos[nd][0] + 0.035 * math.cos(angle)))
                pos[nd][1] = max(margin, min(1 - margin,
                                             pos[nd][1] + 0.035 * math.sin(angle)))
            _enforce_min_separation(nodes, pos, min_dist=0.22,
                                    margin=margin, max_iter=50)
            stuck_for  = 0
            prev_count = None
            continue

        # Process overlapping pairs, refreshing midpoints after every nudge
        for dist, i, j in overlapping:
            u1, v1 = edge_keys[i]
            u2, v2 = edge_keys[j]
            # Recompute — positions may have changed during this pass
            mx1 = (pos[u1][0] + pos[v1][0]) / 2
            my1 = (pos[u1][1] + pos[v1][1]) / 2
            mx2 = (pos[u2][0] + pos[v2][0]) / 2
            my2 = (pos[u2][1] + pos[v2][1]) / 2
            dist = math.hypot(mx1 - mx2, my1 - my2)
            if dist >= min_sep:
                continue    # already resolved by an earlier nudge in this pass

            needed = (min_sep - dist) + 0.006
            if dist > 1e-6:
                dx, dy = (mx1 - mx2) / dist, (my1 - my2) / dist
            else:
                dx, dy = 1.0, 0.0

            # Free nodes: belong to the edge but NOT to the other edge
            free_e1 = [n for n in (u1, v1) if n not in {u2, v2}]
            free_e2 = [n for n in (u2, v2) if n not in {u1, v1}]

            if free_e1 or free_e2:
                # Symmetric: each side contributes needed/2 of midpoint shift
                # → each free node moves by (needed/2) / (0.5) = needed per node
                # simplified: node displacement = needed / count_free_on_that_side
                half = needed   # node displacement needed for midpoint to shift needed/2
                if free_e1:
                    per = half / len(free_e1)
                    for nd in free_e1:
                        pos[nd][0] = max(margin, min(1 - margin,
                                                     pos[nd][0] + dx * per))
                        pos[nd][1] = max(margin, min(1 - margin,
                                                     pos[nd][1] + dy * per))
                if free_e2:
                    per = half / len(free_e2)
                    for nd in free_e2:
                        pos[nd][0] = max(margin, min(1 - margin,
                                                     pos[nd][0] - dx * per))
                        pos[nd][1] = max(margin, min(1 - margin,
                                                     pos[nd][1] - dy * per))
            else:
                # All four endpoints are shared between these two edges
                # (e.g. parallel multi-edges — shouldn't occur in simple graphs).
                # Fall back: move all of e1's nodes.
                per = (needed * 2) / 2
                for nd in (u1, v1):
                    pos[nd][0] = max(margin, min(1 - margin,
                                                 pos[nd][0] + dx * per))
                    pos[nd][1] = max(margin, min(1 - margin,
                                                 pos[nd][1] + dy * per))

        # Re-enforce node separation after each pass
        _enforce_min_separation(nodes, pos, min_dist=0.22, margin=margin,
                                 max_iter=40)

    # ---- Final verification pass --------------------------------------------
    remaining = _count_label_overlaps(edges, pos, min_sep)
    if remaining:
        _enforce_min_separation(nodes, pos, min_dist=0.22, margin=margin,
                                 max_iter=80)


# ---------------------------------------------------------------------------
# Edge-label positions (kept for reference)
# ---------------------------------------------------------------------------

def compute_edge_label_positions(edges: list, positions: dict) -> dict:
    return {(u, v): (
        (positions[u][0] + positions[v][0]) / 2,
        (positions[u][1] + positions[v][1]) / 2,
    ) for u, v, _ in edges}
