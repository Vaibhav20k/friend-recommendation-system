"""Graph data structure module for the social network.

Responsible for:
- Maintaining an unweighted, undirected social network graph using an adjacency list
  (dictionary mapping each user ID to a set of friend user IDs: Dict[str, Set[str]]).
- Adding and removing user nodes with proper cleanup of neighbor references.
- Adding and removing undirected friendship edges with bidirectional consistency.
- Fast O(1) average hash-based verification of user existence and friendship status.
- Retrieving friend neighborhoods, total user counts, and unique friendship counts.

Time Complexities (Average Case):
- add_user: O(1) dictionary key insertion
- remove_user: O(deg(user)) neighbor set discards and dictionary deletion
- add_friendship: O(1) set additions for both endpoints
- remove_friendship: O(1) set discards for both endpoints
- has_user: O(1) dictionary key lookup
- are_friends: O(1) dictionary lookup + set membership test
- get_friends: O(deg(user)) to create and return a protective copy of friend set
- get_all_users: O(V) to create set of user IDs
- get_user_count: O(1) len(dict) lookup
- get_friendship_count: O(V) sum of degree lengths // 2
- get_adjacency_list: O(V + E) deep copy of adjacency structure
- clear: O(1) dictionary reset
"""

from collections import deque
from typing import Any, Dict, List, Set, Tuple


class SocialGraph:
    """An undirected graph representing friendships in a social network.

    Uses an adjacency list representation where nodes are unique user IDs (strings)
    and edges represent bidirectional friendships. The adjacency list is internally
    stored as `Dict[str, Set[str]]` mapping user_id -> Set[friend_id].
    """

    def __init__(self) -> None:
        """Initialize an empty SocialGraph."""
        self._adj: Dict[str, Set[str]] = {}

    def add_user(self, user_id: str) -> bool:
        """Add a user node to the graph if not already present.

        Time Complexity:
            Average Case: O(1) - Python dictionary key lookup and insertion.
            Worst Case: O(V) - in the rare event of severe hash collisions.

        Args:
            user_id: Unique string identifier for the user.

        Returns:
            True if the user node was successfully added, False if the user_id
            already exists in the graph or is invalid (e.g. empty string).
        """
        if not isinstance(user_id, str):
            return False
        user_id = user_id.strip()
        if not user_id or user_id in self._adj:
            return False
        self._adj[user_id] = set()
        return True

    def remove_user(self, user_id: str) -> bool:
        """Remove a user node and all associated friendship edges from the graph.

        Removes the user from the adjacency list and removes `user_id` from
        the neighbor sets of all users they were connected to, maintaining
        bidirectional graph consistency.

        Time Complexity:
            Average Case: O(deg(user_id)) - Iterates through each neighbor of the
            user and performs an O(1) average set discard operation, followed by
            O(1) deletion from the adjacency dictionary.
            Worst Case: O(V) if connected to all vertices.

        Args:
            user_id: Unique string identifier of the user to remove.

        Returns:
            True if the user was found and removed, False otherwise.
        """
        if not isinstance(user_id, str):
            return False
        user_id = user_id.strip()
        if user_id not in self._adj:
            return False

        # Remove user_id from all connected neighbors' sets
        for neighbor in self._adj[user_id]:
            if neighbor in self._adj:
                self._adj[neighbor].discard(user_id)

        # Remove the user node itself
        del self._adj[user_id]
        return True

    def add_friendship(self, user_u: str, user_v: str) -> bool:
        """Add an undirected friendship edge between two users.

        Ensures bidirectional consistency by adding `user_v` to `user_u`'s friend set
        and `user_u` to `user_v`'s friend set. Self-friendships (user_u == user_v)
        are disallowed. If either user does not exist in the graph, they are
        automatically added.

        Time Complexity:
            Average Case: O(1) - Dictionary lookups and set additions are O(1) on average.
            Worst Case: O(V) if hash collision occurs.

        Args:
            user_u: String identifier of the first user.
            user_v: String identifier of the second user.

        Returns:
            True if the friendship was newly created, False if self-friendship,
            invalid identifier, or if the two users are already friends.
        """
        if not isinstance(user_u, str) or not isinstance(user_v, str):
            return False
        user_u = user_u.strip()
        user_v = user_v.strip()
        if not user_u or not user_v or user_u == user_v:
            return False

        # Ensure both users exist or add them automatically if missing
        if user_u not in self._adj:
            self.add_user(user_u)
        if user_v not in self._adj:
            self.add_user(user_v)

        # Check if already friends
        if user_v in self._adj[user_u]:
            return False

        # Add bidirectional edge
        self._adj[user_u].add(user_v)
        self._adj[user_v].add(user_u)
        return True

    def remove_friendship(self, user_u: str, user_v: str) -> bool:
        """Remove an undirected friendship edge between two users.

        Removes the connection in both directions if it exists.

        Time Complexity:
            Average Case: O(1) - Set membership check and discard operations.
            Worst Case: O(deg(u)) on severe hash collision.

        Args:
            user_u: String identifier of the first user.
            user_v: String identifier of the second user.

        Returns:
            True if the friendship existed and was removed, False if either user
            is missing or they were not friends.
        """
        if not isinstance(user_u, str) or not isinstance(user_v, str):
            return False
        user_u = user_u.strip()
        user_v = user_v.strip()
        if user_u not in self._adj or user_v not in self._adj:
            return False

        if user_v not in self._adj[user_u]:
            return False

        self._adj[user_u].discard(user_v)
        self._adj[user_v].discard(user_u)
        return True

    def has_user(self, user_id: str) -> bool:
        """Check if a user exists in the graph.

        Time Complexity:
            Average Case: O(1) hash table lookup.

        Args:
            user_id: String identifier of the user.

        Returns:
            True if user exists in the graph, False otherwise.
        """
        if not isinstance(user_id, str):
            return False
        return user_id.strip() in self._adj

    def are_friends(self, user_u: str, user_v: str) -> bool:
        """Check whether two users are directly connected by a friendship edge.

        Time Complexity:
            Average Case: O(1) - Dict lookup and set membership check.

        Args:
            user_u: String identifier of the first user.
            user_v: String identifier of the second user.

        Returns:
            True if both users exist and are friends, False otherwise.
        """
        if not isinstance(user_u, str) or not isinstance(user_v, str):
            return False
        user_u = user_u.strip()
        user_v = user_v.strip()
        return user_u in self._adj and user_v in self._adj[user_u]

    def get_friends(self, user_id: str) -> Set[str]:
        """Return the set of friend user IDs for a given user.

        Returns a shallow copy of the friend set to protect internal graph state.

        Time Complexity:
            Average Case: O(deg(user_id)) to copy the neighbor set elements.

        Args:
            user_id: String identifier of the user.

        Returns:
            Set of friend user IDs, or an empty set if the user is not found
            or has no friends.
        """
        if not isinstance(user_id, str):
            return set()
        user_id = user_id.strip()
        if user_id not in self._adj:
            return set()
        return set(self._adj[user_id])

    def get_all_users(self) -> Set[str]:
        """Return a set of all user IDs in the graph.

        Time Complexity:
            O(V) where V is the total number of vertices (users).

        Returns:
            Set of all user IDs currently in the graph.
        """
        return set(self._adj.keys())

    def get_user_count(self) -> int:
        """Return the total number of user nodes in the graph.

        Time Complexity:
            O(1) - Reads the cached length of the internal dictionary.

        Returns:
            Number of user nodes.
        """
        return len(self._adj)

    def get_friendship_count(self) -> int:
        """Return the total number of unique undirected friendships in the graph.

        Calculated as the sum of degrees of all vertices divided by 2
        (Handshaking Lemma: sum(deg(v)) = 2 * |E|).

        Time Complexity:
            O(V) where V is the number of vertices in the graph.

        Returns:
            Total count of unique undirected friendships (edges).
        """
        return sum(len(friends) for friends in self._adj.values()) // 2

    def get_adjacency_list(self) -> Dict[str, Set[str]]:
        """Return a copy of the adjacency list.

        Returns a dictionary mapping each user ID to a copy of their friend set,
        ensuring callers cannot inadvertently mutate internal graph structures.

        Time Complexity:
            O(V + E) where V is the number of users and E is the number of friendships.

        Returns:
            Dict[str, Set[str]] representing the complete graph adjacency list.
        """
        return {u: set(friends) for u, friends in self._adj.items()}

    def degree(self, user_id: str) -> int:
        """Return the degree (number of friends) of a given user.

        Time Complexity:
            O(1) average lookup.

        Args:
            user_id: Unique string identifier for the user.

        Returns:
            Integer degree, or 0 if user does not exist in graph.
        """
        if not isinstance(user_id, str):
            return 0
        user_id = user_id.strip()
        return len(self._adj.get(user_id, set()))

    def neighbors(self, user_id: str) -> Set[str]:
        """Return the set of neighbor (friend) user IDs for a given user.

        Alias for get_friends(user_id). Returns a defensive copy.

        Args:
            user_id: Unique string identifier for the user.

        Returns:
            Set of friend user IDs, or empty set if user not found.
        """
        return self.get_friends(user_id)

    def edges(self) -> List[Tuple[str, str]]:
        """Return a sorted list of unique undirected edges in the graph.

        Each edge is represented as a normalized tuple (min(u, v), max(u, v)).

        Time Complexity:
            O(V + E log E) - Traverses adjacency list and sorts unique edges.

        Returns:
            List of unique undirected edge tuples sorted deterministically.
        """
        seen: Set[Tuple[str, str]] = set()
        for u, nbrs in self._adj.items():
            for v in nbrs:
                edge = (min(u, v), max(u, v))
                seen.add(edge)

        def edge_sort_key(e: Tuple[str, str]) -> Tuple[int, int, str, int, int, str]:
            u, v = e[0], e[1]
            u_key = (0, int(u), u) if u.isdigit() else (1, 0, u)
            v_key = (0, int(v), v) if v.isdigit() else (1, 0, v)
            return u_key + v_key

        return sorted(seen, key=edge_sort_key)

    def connected_components(self) -> List[List[str]]:
        """Compute all connected components in the graph using manual BFS traversal.

        Does NOT use NetworkX; implemented in pure Python from first principles.

        Time Complexity:
            O(V + E) - Standard BFS component traversal across all vertices.

        Returns:
            List of connected components. Each component is a sorted list of user IDs.
            Components are ordered by size descending, tie-broken by first user ID.
        """
        visited: Set[str] = set()
        components: List[List[str]] = []

        # Sort vertices for deterministic iteration
        def node_sort_key(u: str) -> Tuple[int, int, str]:
            return (0, int(u), u) if u.isdigit() else (1, 0, u)

        all_nodes = sorted(self._adj.keys(), key=node_sort_key)

        for node in all_nodes:
            if node not in visited:
                component: List[str] = []
                queue: deque[str] = deque([node])
                visited.add(node)

                while queue:
                    curr = queue.popleft()
                    component.append(curr)

                    for nbr in sorted(self._adj.get(curr, set()), key=node_sort_key):
                        if nbr not in visited:
                            visited.add(nbr)
                            queue.append(nbr)

                component.sort(key=node_sort_key)
                components.append(component)

        # Sort components: largest first, then by first node ID
        components.sort(key=lambda c: (-len(c), node_sort_key(c[0]) if c else (1, 0, "")))
        return components

    def clear(self) -> None:
        """Reset the graph to an empty state, clearing all nodes and edges.

        Time Complexity:
            O(1) dictionary clear.
        """
        self._adj.clear()

    def get_network_metrics(self) -> Dict[str, Any]:
        """Return network-level graph metrics for this graph."""
        return get_network_metrics(self)

    def __contains__(self, user_id: str) -> bool:
        """Enable pythonic 'user_id in graph' syntax."""
        return self.has_user(user_id)

    def __len__(self) -> int:
        """Enable pythonic 'len(graph)' returning user count."""
        return self.get_user_count()

    def __repr__(self) -> str:
        """Return a string representation of the graph summary."""
        return (
            f"SocialGraph(users={self.get_user_count()}, "
            f"friendships={self.get_friendship_count()})"
        )


def get_network_metrics(graph: SocialGraph) -> Dict[str, Any]:
    """Calculate key graph theory and topological metrics for a social network.

    Metrics calculated:
    - total_users: Number of vertices |V|
    - total_friendships: Number of unique undirected edges |E|
    - density: Ratio of actual edges to maximum possible edges in simple undirected graph:
               2 * |E| / (|V| * (|V| - 1)). Returns 0.0 if |V| < 2.
    - average_degree: Average number of connections per node: 2 * |E| / |V|.
    - isolated_users: Deterministically sorted list of user IDs with degree 0.
    - isolated_count: Count of isolated users.
    - max_degree: The maximum vertex degree present in the network.
    - max_degree_users: List of (user_id, degree) for user(s) attaining the maximum degree.
    - degrees: Dictionary mapping user_id -> degree.

    Time Complexity:
        O(V + E) - Reads adjacency list degrees and calculates statistics.
    Space Complexity:
        O(V) auxiliary memory for degrees dictionary and isolate collections.

    Args:
        graph: The SocialGraph instance to analyze.

    Returns:
        Dict[str, Any] containing all calculated network metrics.
    """
    v = graph.get_user_count()
    e = graph.get_friendship_count()
    adj = graph.get_adjacency_list()

    degrees: Dict[str, int] = {uid: len(friends) for uid, friends in adj.items()}
    isolated_users: List[str] = sorted([uid for uid, deg in degrees.items() if deg == 0])

    density: float = 0.0
    if v >= 2:
        max_possible_edges = v * (v - 1) / 2
        density = e / max_possible_edges

    avg_degree: float = 0.0
    if v > 0:
        avg_degree = (2.0 * e) / v

    max_deg = max(degrees.values()) if degrees else 0
    max_degree_users = sorted(
        [(uid, deg) for uid, deg in degrees.items() if deg == max_deg]
    )

    components = graph.connected_components()

    return {
        "total_users": v,
        "total_friendships": e,
        "density": density,
        "average_degree": avg_degree,
        "isolated_users": isolated_users,
        "isolated_count": len(isolated_users),
        "max_degree": max_deg,
        "max_degree_users": max_degree_users,
        "degrees": degrees,
        "connected_components": components,
        "component_count": len(components),
    }

