"""Breadth-First Search (BFS) and Connection Explorer module.

Responsible for:
- Manual BFS traversal using collections.deque.
- Tracking visited nodes and parent relationships for path reconstruction.
- Finding the shortest connection path and degrees of separation between any two users.
- Handling disconnected components and edge cases.
"""

from collections import deque
from typing import Dict, List, Optional, Set, Tuple

from core.graph import SocialGraph


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
           in the queue are monotonically non-decreasing and differ by at most 1:
           [d, d, ..., d, d+1, d+1, ..., d+1].
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
        - Vertex Processing:
          Each reachable user node is enqueued at most once and dequeued at most once:
          O(V) operations where V = |V| is the number of vertices in the network.
        - Edge Exploration:
          For each visited node, its incident edges are examined. In an undirected graph,
          each edge {u, v} is considered at most twice (once from u, once from v):
          O(sum_{v in V} deg(v)) = O(2E) = O(E).
        - Deterministic Neighbor Sorting:
          Sorting neighbors for deterministic tie-breaking takes O(deg(u) log(deg(u))).
          Across all nodes, sum_{u in V} deg(u) log(deg(u)) <= O(E log(d_max)) <= O(E log V).
        - Path Reconstruction:
          Backtracking from target_user to start_user through `parent` takes at most V steps:
          O(V).
        - Total Time Complexity:
          O(V + E) (or O(V + E log(d_max)) with sorted neighbors), which is optimal
          for unweighted shortest-path exploration.

    Space Complexity:
        - FIFO Queue: Holds at most O(V) nodes at any time.
        - Visited Set: Stores at most O(V) node identifiers.
        - Parent Map: Stores at most O(V) predecessor pointers.
        - Total Space Complexity: O(V) auxiliary memory.

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
    start_user = str(start_user)
    target_user = str(target_user)

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

        for neighbor in sorted(graph.get_friends(current)):
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

