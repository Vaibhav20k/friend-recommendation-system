"""Breadth-First Search (BFS) and Connection Explorer module.

Responsible for:
- Manual BFS traversal using collections.deque.
- Tracking visited nodes and parent relationships for path reconstruction.
- Finding the shortest connection path and degrees of separation between any two users.
- Computing LinkedIn-style network degree levels (1st, 2nd, 3rd degree connections).
- Step-by-step generator for interactive BFS visualization and narration.
- Academic verification oracle cross-checking manual BFS against NetworkX.
"""

from collections import deque
from typing import Any, Dict, Iterator, List, Optional, Set, Tuple

from core.graph import SocialGraph


def _node_sort_key(u: str) -> Tuple[int, int, str]:
    """Sort key for deterministic node ordering (numeric if possible, else string)."""
    return (0, int(u), u) if u.isdigit() else (1, 0, u)


def find_shortest_connection(
    graph: SocialGraph,
    start_user: str,
    target_user: str,
) -> Tuple[Optional[List[str]], int]:
    """Find the shortest connection path and degrees of separation between two users using BFS.

    Breadth-First Search (BFS) traverses the social network layer by layer (level order),
    expanding all vertices at distance d before exploring vertices at distance d + 1.
    In an unweighted graph where every friendship edge has an identical cost/weight of 1,
    the first time `target_user` is dequeued, the path traversed from `start_user` is
    guaranteed to have the minimal number of edges (shortest path).

    Why BFS Guarantees Shortest Path in Unweighted Graphs:
        1. Layer-by-Layer / FIFO Exploration:
           BFS maintains a FIFO queue (`collections.deque`). If node u is discovered before
           node v, then distance(start_user, u) <= distance(start_user, v). Distances of nodes
           in the queue are monotonically non-decreasing and differ by at most 1.
        2. First-Encounter Optimality:
           Since every edge represents 1 unit of distance (degree of separation), any path
           with k edges has total weight k. BFS explores every path of length k before
           attempting any path of length k + 1. Therefore, when `target_user` is first dequeued,
           it is reached via a path of minimal length. No shorter path could possibly exist.
        3. Cycle Prevention via Visited Set:
           The `visited` set ensures no node is processed more than once, guarding against
           infinite loops in cyclic graphs and preventing suboptimal paths from overwriting
           the first-discovered shortest route.

    Time Complexity Analysis:
        - Vertex Processing: O(V) operations.
        - Edge Exploration: O(E) operations.
        - Deterministic Neighbor Sorting: O(deg(u) log(deg(u))).
        - Path Reconstruction: O(V).
        - Total Time Complexity: O(V + E log(d_max)) optimal for unweighted graphs.
    Space Complexity: O(V) auxiliary memory for queue, visited set, and parent map.

    Args:
        graph: The SocialGraph instance to search.
        start_user: Unique string identifier of the starting user.
        target_user: Unique string identifier of the target user.

    Returns:
        Tuple[Optional[List[str]], int]:
            - (path, distance): Where `path` is the list of user IDs from start_user
              to target_user inclusive, and `distance` is the number of edges (hops).
            - ([start_user], 0) if start_user == target_user and user exists in graph.
            - (None, -1) if either user does not exist or no connecting path exists.
    """
    start_user = str(start_user).strip()
    target_user = str(target_user).strip()

    if not graph.has_user(start_user) or not graph.has_user(target_user):
        return (None, -1)

    if start_user == target_user:
        return ([start_user], 0)

    queue: deque[str] = deque([start_user])
    visited: Set[str] = {start_user}
    parent: Dict[str, str] = {}
    target_reached: bool = False

    while queue:
        current: str = queue.popleft()

        if current == target_user:
            target_reached = True
            break

        for neighbor in sorted(graph.get_friends(current), key=_node_sort_key):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                queue.append(neighbor)

    if target_reached:
        path: List[str] = [target_user]
        curr: str = target_user
        while curr != start_user:
            curr = parent[curr]
            path.append(curr)
        path.reverse()
        distance: int = len(path) - 1
        return (path, distance)

    return (None, -1)


def bfs_levels(graph: SocialGraph, src: str) -> Dict[int, List[str]]:
    """Group all reachable users by their degrees of separation (level) from src.

    Provides a LinkedIn-style network breakdown:
    - Level 1: Direct friends
    - Level 2: Friends of friends
    - Level 3+: Extended network

    Time Complexity:
        O(V + E) level-order BFS traversal.

    Args:
        graph: The SocialGraph instance.
        src: Starting user identifier.

    Returns:
        Dict[int, List[str]] mapping degree level (1, 2, 3...) to deterministically sorted user IDs.
        Returns empty dictionary if src does not exist in graph or has no reachable neighbors.
    """
    src = str(src).strip()
    if not graph.has_user(src):
        return {}

    levels: Dict[int, List[str]] = {}
    queue: deque[Tuple[str, int]] = deque([(src, 0)])
    visited: Set[str] = {src}

    while queue:
        curr, dist = queue.popleft()
        if dist > 0:
            if dist not in levels:
                levels[dist] = []
            levels[dist].append(curr)

        for nbr in sorted(graph.get_friends(curr), key=_node_sort_key):
            if nbr not in visited:
                visited.add(nbr)
                queue.append((nbr, dist + 1))

    for d in levels:
        levels[d].sort(key=_node_sort_key)

    return levels


def bfs_steps(graph: SocialGraph, src: str, dst: str) -> Iterator[Dict[str, Any]]:
    """Yield snapshot dictionaries representing step-by-step BFS progress.

    Drives the step-by-step interactive BFS visualizer.

    Each yielded snapshot contains:
        - step: Integer step count (0, 1, 2...)
        - current: User ID currently dequeued and active (None at initialization)
        - queue: List of user IDs currently in FIFO queue
        - visited: Set of all discovered user IDs
        - parent: Dict mapping discovered child -> predecessor
        - level: Dict mapping discovered node -> distance from src
        - found: True if dst reached, False otherwise
        - message: Human-readable narrative explaining this specific step
        - path: Shortest path list if found, else None

    Args:
        graph: SocialGraph instance.
        src: Starting user identifier.
        dst: Destination user identifier.

    Yields:
        Dict[str, Any] snapshot per step.
    """
    src = str(src).strip()
    dst = str(dst).strip()

    if not graph.has_user(src) or not graph.has_user(dst):
        yield {
            "step": 0,
            "current": None,
            "queue": [],
            "visited": set(),
            "parent": {},
            "level": {},
            "found": False,
            "message": "Source or destination user does not exist in network.",
            "path": None,
        }
        return

    if src == dst:
        yield {
            "step": 0,
            "current": src,
            "queue": [src],
            "visited": {src},
            "parent": {},
            "level": {src: 0},
            "found": True,
            "message": f"Start student '{src}' is the target student. Distance is 0 hops.",
            "path": [src],
        }
        return

    queue: deque[str] = deque([src])
    visited: Set[str] = {src}
    parent: Dict[str, str] = {}
    level: Dict[str, int] = {src: 0}
    step = 0

    # Yield step 0: Initial state
    yield {
        "step": step,
        "current": None,
        "queue": list(queue),
        "visited": set(visited),
        "parent": dict(parent),
        "level": dict(level),
        "found": False,
        "message": f"Initialized BFS queue at source '{src}'.",
        "path": None,
    }

    while queue:
        step += 1
        curr = queue.popleft()

        if curr == dst:
            path = [dst]
            back = dst
            while back != src:
                back = parent[back]
                path.append(back)
            path.reverse()

            yield {
                "step": step,
                "current": curr,
                "queue": list(queue),
                "visited": set(visited),
                "parent": dict(parent),
                "level": dict(level),
                "found": True,
                "message": f"🎯 Target '{dst}' dequeued! Shortest connection established in {len(path) - 1} hops.",
                "path": path,
            }
            return

        added_neighbors: List[str] = []
        for nbr in sorted(graph.get_friends(curr), key=_node_sort_key):
            if nbr not in visited:
                visited.add(nbr)
                parent[nbr] = curr
                level[nbr] = level[curr] + 1
                queue.append(nbr)
                added_neighbors.append(nbr)

        if added_neighbors:
            msg = f"Dequeued '{curr}' (level {level[curr]}). Enqueued new unvisited neighbors: {', '.join(added_neighbors)}."
        else:
            msg = f"Dequeued '{curr}' (level {level[curr]}). No new unvisited neighbors found."

        yield {
            "step": step,
            "current": curr,
            "queue": list(queue),
            "visited": set(visited),
            "parent": dict(parent),
            "level": dict(level),
            "found": False,
            "message": msg,
            "path": None,
        }

    # Queue exhausted without finding target
    step += 1
    yield {
        "step": step,
        "current": None,
        "queue": [],
        "visited": set(visited),
        "parent": dict(parent),
        "level": dict(level),
        "found": False,
        "message": f"❌ Queue is empty. No connection path exists between '{src}' and '{dst}' (disconnected components).",
        "path": None,
    }


def verify_with_networkx(graph: SocialGraph, src: str, dst: str) -> bool:
    """Verify manual BFS shortest connection against NetworkX.

    Academic Integrity Note:
        NetworkX is used strictly as an independent automated oracle to verify
        the correctness of our hand-written BFS algorithm. NetworkX is NEVER used
        to produce the actual path or results shown to users.

    Args:
        graph: The SocialGraph instance.
        src: Starting user ID.
        dst: Target user ID.

    Returns:
        True if manual BFS agrees with NetworkX nx.shortest_path_length
        (or if both agree that no connecting path exists), False otherwise.
    """
    import networkx as nx

    path, manual_dist = find_shortest_connection(graph, src, dst)

    # Reconstruct NetworkX Graph solely for validation check
    G = nx.Graph()
    for u in graph.get_all_users():
        G.add_node(u)
    for u, nbrs in graph.get_adjacency_list().items():
        for v in nbrs:
            G.add_edge(u, v)

    src_s = str(src).strip()
    dst_s = str(dst).strip()

    if not G.has_node(src_s) or not G.has_node(dst_s):
        return manual_dist == -1

    has_nx_path = nx.has_path(G, src_s, dst_s)

    if not has_nx_path:
        return manual_dist == -1

    nx_dist = nx.shortest_path_length(G, src_s, dst_s)
    return manual_dist == nx_dist
