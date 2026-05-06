import heapq
from graph.graph import Graph, SolveStep, WorkingStep, Question


def solve(graph: Graph, seed: int) -> Question:
    nodes = graph.nodes
    dist = {n: float('inf') for n in nodes}
    prev = {n: None for n in nodes}
    dist[graph.start] = 0
    pq = [(0, graph.start)]

    # Record every relaxation event in chronological order.
    # The start node is treated as its own first relaxation at distance 0.
    relax_events = [(graph.start, 0, None)]

    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        adj = [(v, w) for a, b, w in graph.edges
               for v in ([b] if a == u else [a] if b == u else [])]
        for v, w in adj:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))
                relax_events.append((v, nd, u))

    # is_final=True only for the event whose distance matches the node's settled value.
    working_steps = [
        WorkingStep(node=n, distance=d, previous=p, is_final=(dist[n] == d))
        for n, d, p in relax_events
    ]

    # Build alphabetical step table
    steps = []
    for node in sorted(nodes):
        steps.append(SolveStep(
            node=node,
            distance=dist[node],
            previous=prev[node],
        ))

    # Reconstruct path
    path = []
    cur = graph.goal
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    path.reverse()

    return Question(
        graph=graph,
        algorithm='Dijkstra',
        steps=steps,
        final_path=path,
        final_distance=dist[graph.goal],
        seed=seed,
        working_steps=working_steps,
    )
