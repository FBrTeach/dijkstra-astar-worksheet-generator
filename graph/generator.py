import random
import heapq
from config import DIFFICULTY_PRESETS, NODE_LABELS, MAX_RETRIES
from graph.graph import Graph
from graph.layout import generate_positions_with_edges


def _dijkstra_distances(nodes, adj, start):
    dist = {n: float('inf') for n in nodes}
    dist[start] = 0
    pq = [(0, start)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    return dist


def _astar_g_values(nodes, adj, start, goal, heuristics):
    g = {n: float('inf') for n in nodes}
    g[start] = 0
    pq = [(heuristics[start], 0, start)]
    settled = set()
    while pq:
        f, gval, u = heapq.heappop(pq)
        if u in settled:
            continue
        settled.add(u)
        if u == goal:
            break
        for v, w in adj[u]:
            if v in settled:
                continue
            ng = gval + w
            if ng < g[v]:
                g[v] = ng
                heapq.heappush(pq, (ng + heuristics[v], ng, v))
    return g


def _build_adj(nodes, edges):
    adj = {n: [] for n in nodes}
    for u, v, w in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))
    return adj


def _all_reachable(nodes, adj, start):
    visited, stack = set(), [start]
    while stack:
        n = stack.pop()
        if n in visited:
            continue
        visited.add(n)
        for nb, _ in adj[n]:
            stack.append(nb)
    return visited == set(nodes)


def _no_ties(values: list) -> bool:
    finite = [v for v in values if v != float('inf')]
    return len(finite) == len(set(finite))


def _pick_start_goal(nodes, edges, adj, rng):
    """
    Return (start, goal, dist_from_start) where:
      - start and goal are not directly connected by an edge
      - goal is not the closest reachable node to start
    Returns (None, None, None) if no valid pair exists.
    """
    adj_set = {(u, v) for u, v, _ in edges} | {(v, u) for u, v, _ in edges}
    shuffled = list(nodes)
    rng.shuffle(shuffled)

    for s in shuffled:
        dists = _dijkstra_distances(nodes, adj, s)
        reachable = [(n, d) for n, d in dists.items()
                     if n != s and d != float('inf')]
        if not reachable:
            continue

        min_dist = min(d for _, d in reachable)

        valid_goals = [
            n for n, d in reachable
            if (s, n) not in adj_set   # not directly adjacent
            and d > min_dist            # not the closest node
        ]
        if not valid_goals:
            continue

        if not _no_ties(list(dists.values())):
            continue

        goal = rng.choice(valid_goals)
        return s, goal, dists

    return None, None, None


def _generate_graph_attempt(rng: random.Random, preset: dict,
                             algorithm: str) -> Graph:
    node_count = rng.randint(*preset['node_count'])
    nodes = NODE_LABELS[:node_count]
    lo, hi = preset['weight_range']
    extra = rng.randint(*preset['extra_edges'])

    # Random spanning tree
    shuffled = list(nodes)
    rng.shuffle(shuffled)
    edges = []
    in_tree = {shuffled[0]}
    for node in shuffled[1:]:
        parent = rng.choice(list(in_tree))
        edges.append((parent, node, rng.randint(lo, hi)))
        in_tree.add(node)

    # Extra edges
    existing = {(u, v) for u, v, _ in edges} | {(v, u) for u, v, _ in edges}
    added = 0
    for _ in range(300):
        if added >= extra:
            break
        u, v = rng.sample(nodes, 2)
        if (u, v) not in existing:
            edges.append((u, v, rng.randint(lo, hi)))
            existing.add((u, v))
            existing.add((v, u))
            added += 1

    adj = _build_adj(nodes, edges)

    if not _all_reachable(nodes, adj, nodes[0]):
        return None

    start, goal, dist_from_start = _pick_start_goal(nodes, edges, adj, rng)
    if start is None:
        return None

    heuristics = None
    if algorithm == 'A*':
        dist_to_goal = _dijkstra_distances(nodes, adj, goal)
        if any(dist_to_goal[n] == float('inf') for n in nodes):
            return None

        heuristics = {}
        for n in nodes:
            if n == goal:
                heuristics[n] = 0
            else:
                factor = rng.uniform(0.65, 0.92)
                heuristics[n] = max(1, int(dist_to_goal[n] * factor))

        g_vals = _astar_g_values(nodes, adj, start, goal, heuristics)
        discovered_g = [v for v in g_vals.values() if v != float('inf')]
        if not _no_ties(discovered_g):
            return None
        if not _no_ties(list(heuristics.values())):
            return None

    positions = generate_positions_with_edges(list(nodes), edges, rng)
    return Graph(nodes=list(nodes), edges=edges, positions=positions,
                 start=start, goal=goal, heuristics=heuristics)


def generate_graph(difficulty: str, algorithm: str, seed: int) -> Graph:
    preset = DIFFICULTY_PRESETS[difficulty]
    rng = random.Random(seed)
    for _ in range(MAX_RETRIES):
        g = _generate_graph_attempt(rng, preset, algorithm)
        if g is not None:
            return g
    raise RuntimeError(
        f"Could not generate a valid graph after {MAX_RETRIES} attempts "
        f"(seed={seed}, difficulty={difficulty}, algorithm={algorithm}). "
        "Try a different seed."
    )
