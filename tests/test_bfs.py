"""Unit tests for Breadth-First Search traversal and shortest paths (Phase 4)."""

import pytest
from core.graph import SocialGraph
from core.bfs import find_shortest_connection


@pytest.fixture
def social_network_graph() -> SocialGraph:
    """Fixture providing the complete 12-user social graph from data/users.json.

    Graph topology:
        Alice (1)  ─── Bob (2)   ─── Emma (5)  ─── Hannah (8) ─── Ian (9) ─── Kelly (11)
          │      ＼      │          │                 ＼         ／             │
          │        ＼    │          │                   ＼     ／               │
          │          ＼  │          │                     Grace (7)             │
        Charlie (3) ─── David (4) ── Frank (6) ─────────────────────────── Jack (10)

        Liam (12) [Disconnected / Isolated User]
    """
    graph = SocialGraph()
    for user_id in range(1, 13):
        graph.add_user(str(user_id))

    friendships = [
        ("1", "2"),   # Alice - Bob
        ("1", "3"),   # Alice - Charlie
        ("1", "4"),   # Alice - David
        ("2", "5"),   # Bob - Emma
        ("2", "6"),   # Bob - Frank
        ("3", "5"),   # Charlie - Emma
        ("3", "7"),   # Charlie - Grace
        ("4", "6"),   # David - Frank
        ("5", "8"),   # Emma - Hannah
        ("6", "10"),  # Frank - Jack
        ("7", "8"),   # Grace - Hannah
        ("7", "9"),   # Grace - Ian
        ("8", "9"),   # Hannah - Ian
        ("9", "11"),  # Ian - Kelly
        ("10", "11")  # Jack - Kelly
    ]
    for u1, u2 in friendships:
        graph.add_friendship(u1, u2)

    return graph


def test_direct_connection_distance_1(social_network_graph: SocialGraph):
    """Test shortest connection between directly connected friends (distance 1)."""
    # Alice (1) to Bob (2)
    path, distance = find_shortest_connection(social_network_graph, "1", "2")
    assert path == ["1", "2"]
    assert distance == 1

    # Alice (1) to Charlie (3)
    path, distance = find_shortest_connection(social_network_graph, "1", "3")
    assert path == ["1", "3"]
    assert distance == 1

    # Alice (1) to David (4)
    path, distance = find_shortest_connection(social_network_graph, "1", "4")
    assert path == ["1", "4"]
    assert distance == 1


def test_multi_hop_connection(social_network_graph: SocialGraph):
    """Test multi-hop shortest paths across varying degrees of separation."""
    # Alice (1) to Grace (7): distance 2 (Alice -> Charlie -> Grace)
    path_grace, dist_grace = find_shortest_connection(social_network_graph, "1", "7")
    assert path_grace == ["1", "3", "7"]
    assert dist_grace == 2

    # Alice (1) to Ian (9): distance 3 (Alice -> Charlie -> Grace -> Ian)
    path_ian, dist_ian = find_shortest_connection(social_network_graph, "1", "9")
    assert path_ian == ["1", "3", "7", "9"]
    assert dist_ian == 3

    # Alice (1) to Kelly (11): distance 4 (Alice -> Bob -> Frank -> Jack -> Kelly)
    path_kelly, dist_kelly = find_shortest_connection(social_network_graph, "1", "11")
    assert dist_kelly == 4
    assert path_kelly == ["1", "2", "6", "10", "11"]
    assert len(path_kelly) == dist_kelly + 1

    # Verify that every consecutive pair in path forms a valid edge
    for i in range(len(path_kelly) - 1):
        assert social_network_graph.are_friends(path_kelly[i], path_kelly[i + 1])


def test_disconnected_user(social_network_graph: SocialGraph):
    """Test connection queries involving an isolated / disconnected component."""
    # Alice (1) to Liam (12)
    path, distance = find_shortest_connection(social_network_graph, "1", "12")
    assert path is None
    assert distance == -1

    # Liam (12) to Alice (1)
    path_rev, dist_rev = find_shortest_connection(social_network_graph, "12", "1")
    assert path_rev is None
    assert dist_rev == -1


def test_same_user_identity(social_network_graph: SocialGraph):
    """Test connection query where start_user and target_user are identical."""
    # Alice to Alice
    path, distance = find_shortest_connection(social_network_graph, "1", "1")
    assert path == ["1"]
    assert distance == 0

    # Isolated user Liam to Liam
    path_liam, dist_liam = find_shortest_connection(social_network_graph, "12", "12")
    assert path_liam == ["12"]
    assert dist_liam == 0


def test_non_existent_users(social_network_graph: SocialGraph):
    """Test connection queries with missing or non-existent user IDs."""
    # Non-existent start user
    path, distance = find_shortest_connection(social_network_graph, "999", "1")
    assert path is None
    assert distance == -1

    # Non-existent target user
    path, distance = find_shortest_connection(social_network_graph, "1", "999")
    assert path is None
    assert distance == -1

    # Both users non-existent
    path, distance = find_shortest_connection(social_network_graph, "unknown_a", "unknown_b")
    assert path is None
    assert distance == -1

    # Empty string user ID
    path, distance = find_shortest_connection(social_network_graph, "", "1")
    assert path is None
    assert distance == -1


def test_path_symmetry(social_network_graph: SocialGraph):
    """Verify that distance is symmetric in an undirected graph."""
    _, dist_forward = find_shortest_connection(social_network_graph, "1", "10")
    _, dist_backward = find_shortest_connection(social_network_graph, "10", "1")
    assert dist_forward == dist_backward
    assert dist_forward == 3


def test_bfs_empty_graph():
    """BFS on an empty graph should return (None, -1)."""
    empty_graph = SocialGraph()
    path, dist = find_shortest_connection(empty_graph, "A", "B")
    assert path is None
    assert dist == -1

    path_self, dist_self = find_shortest_connection(empty_graph, "A", "A")
    assert path_self is None
    assert dist_self == -1


def test_bfs_single_node_graph():
    """BFS on single-node graph: self identity is 0, missing target is -1."""
    single_graph = SocialGraph()
    single_graph.add_user("solo")

    path, dist = find_shortest_connection(single_graph, "solo", "solo")
    assert path == ["solo"]
    assert dist == 0

    path_miss, dist_miss = find_shortest_connection(single_graph, "solo", "other")
    assert path_miss is None
    assert dist_miss == -1


def test_bfs_two_disconnected_nodes():
    """Two isolated nodes in graph have no connecting path."""
    graph = SocialGraph()
    graph.add_user("A")
    graph.add_user("B")

    path, dist = find_shortest_connection(graph, "A", "B")
    assert path is None
    assert dist == -1


def test_bfs_linear_graph():
    """BFS on line graph 1-2-3-4-5 should find the single direct line path."""
    graph = SocialGraph()
    for i in range(1, 5):
        graph.add_friendship(str(i), str(i + 1))

    path, dist = find_shortest_connection(graph, "1", "5")
    assert path == ["1", "2", "3", "4", "5"]
    assert dist == 4


def test_bfs_cyclic_graph_c4():
    """BFS terminates and avoids infinite loops on 4-cycle C4."""
    graph = SocialGraph()
    # Square: 1-2, 2-3, 3-4, 4-1
    graph.add_friendship("1", "2")
    graph.add_friendship("2", "3")
    graph.add_friendship("3", "4")
    graph.add_friendship("4", "1")

    # Shortest path from 1 to 3 has distance 2
    path, dist = find_shortest_connection(graph, "1", "3")
    assert dist == 2
    assert len(path) == 3
    assert path[0] == "1" and path[-1] == "3"


def test_bfs_star_graph():
    """BFS on star graph S5: leaves are distance 2 apart via center."""
    graph = SocialGraph()
    center = "0"
    leaves = ["1", "2", "3", "4", "5"]
    for leaf in leaves:
        graph.add_friendship(center, leaf)

    path, dist = find_shortest_connection(graph, "1", "5")
    assert path == ["1", "0", "5"]
    assert dist == 2


def test_bfs_complete_graph_k4():
    """BFS on complete graph K4: all pairs of distinct nodes are distance 1."""
    graph = SocialGraph()
    nodes = ["A", "B", "C", "D"]
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            graph.add_friendship(nodes[i], nodes[j])

    for i in range(len(nodes)):
        for j in range(len(nodes)):
            if i != j:
                path, dist = find_shortest_connection(graph, nodes[i], nodes[j])
                assert dist == 1
                assert path == [nodes[i], nodes[j]]


def test_networkx_agreement_on_50_random_pairs():
    """Verify exact agreement between manual BFS and NetworkX oracle across 50 random pairs on a generated graph."""
    import random
    from data.generate_dataset import generate_campus_dataset
    from core.bfs import verify_with_networkx

    dataset = generate_campus_dataset(num_students=50, seed=123)
    graph = SocialGraph()
    for u in dataset["users"]:
        graph.add_user(u["id"])
    for u, v in dataset["friendships"]:
        graph.add_friendship(u, v)

    all_users = list(graph.get_all_users())
    random.seed(999)
    for _ in range(50):
        u = random.choice(all_users)
        v = random.choice(all_users)
        assert verify_with_networkx(graph, u, v) is True

