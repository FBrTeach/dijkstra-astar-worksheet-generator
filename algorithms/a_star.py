import heapq
from graph.graph import Graph, SolveStep, Question


def solve(graph: Graph, seed: int) -> Question:
    nodes = graph.nodes
    h = graph.heuristics
    g = {n: float('inf') for n in nodes}
    prev = {n: None for n in nodes}
    g[graph.start] = 0
    # pq entries: (f, g, node) — g used as tiebreaker
    pq = [(h[graph.start], 0, graph.start)]
    settled = set()

    while pq:
        f, gval, u = heapq.heappop(pq)
        if u in settled:
            continue
        settled.add(u)
        if u == graph.goal:
            break

        adj = [(v, w) for a, b, w in graph.edges
               for v in ([b] if a == u else [a] if b == u else [])]
        for v, w in adj:
            if v in settled:
                continue
            ng = gval + w
            if ng < g[v]:
                g[v] = ng
                prev[v] = u
                nf = ng + h[v]
                heapq.heappush(pq, (nf, ng, v))

    # Build alphabetical step table (only nodes that were reached)
    steps = []
    for node in sorted(nodes):
        if g[node] == float('inf'):
            continue
        steps.append(SolveStep(
            node=node,
            distance=g[node],
            previous=prev[node],
            heuristic=h[node],
            f_score=g[node] + h[node],
        ))

    # Reconstruct path
    path = []
    cur = graph.goal
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    path.reverse()

    n_settled = len(settled)
    n_total = len(nodes)
    note = (f'A* settled {n_settled} of {n_total} nodes to find the path; '
            f"Dijkstra's would have settled all {n_total}.")

    return Question(
        graph=graph,
        algorithm='A*',
        steps=steps,
        final_path=path,
        final_distance=g[graph.goal],
        seed=seed,
        comparison_note=note,
    )
