from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Graph:
    nodes: list
    edges: list          # list of (u, v, weight) — undirected
    positions: dict      # node -> (x, y) in [0,1]^2
    start: str
    goal: str
    heuristics: Optional[dict] = None   # node -> int, only for A*


@dataclass
class SolveStep:
    node: str
    distance: int
    previous: Optional[str]
    heuristic: Optional[int] = None
    f_score: Optional[int] = None


@dataclass
class WorkingStep:
    """One relaxation event recorded during Dijkstra's algorithm."""
    node: str
    distance: int
    previous: Optional[str]
    is_final: bool = True   # False = superseded by a later (smaller) relaxation


@dataclass
class Question:
    graph: Graph
    algorithm: str       # 'Dijkstra' or 'A*'
    steps: list          # list[SolveStep], alphabetical by node
    final_path: list     # list[str] from start to goal
    final_distance: int
    seed: int
    difficulty: str = 'Medium'
    working_steps: list = field(default_factory=list)  # chronological relaxations (Dijkstra)
    comparison_note: str = ''                           # A* efficiency note
