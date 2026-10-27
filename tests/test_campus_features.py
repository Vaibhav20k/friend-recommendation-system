"""Unit tests for CampusConnect upgrades: BFS levels, BFS steps, NetworkX verification,
connected components, Jaccard similarity recommendations, and student profile management."""

import pytest
from core.graph import SocialGraph
from core.user_manager import UserManager
from core.bfs import bfs_levels, bfs_steps, find_shortest_connection, verify_with_networkx
from core.recommendation import calculate_jaccard_similarity, get_friend_recommendations


@pytest.fixture
def sample_campus_graph():
    """Graph with 3 components:
    - Main component: 1 (Alice), 2 (Bob), 3 (Charlie), 4 (David), 5 (Emma)
    - Small separate component: 6 (Frank), 7 (Grace)
    - Isolated node: 8 (Hannah)
    """
    g = SocialGraph()
    for uid in ["1", "2", "3", "4", "5", "6", "7", "8"]:
        g.add_user(uid)

    # Main component
    g.add_friendship("1", "2")
    g.add_friendship("1", "3")
    g.add_friendship("2", "4")
    g.add_friendship("3", "4")
    g.add_friendship("4", "5")

    # Small component
    g.add_friendship("6", "7")

    # 8 is isolated
    return g


@pytest.fixture
def sample_campus_manager():
    """UserManager populated with student profiles including branches and interests."""
    um = UserManager()
    um.add_user("1", "Alice Roy", username="alice", branch="CSE", year=2, interests=["coding", "music"])
    um.add_user("2", "Bob Patel", username="bob", branch="CSE", year=2, interests=["coding", "gaming"])
    um.add_user("3", "Charlie Das", username="charlie", branch="ECE", year=2, interests=["music", "robotics"])
    um.add_user("4", "David Rao", username="david", branch="CSE", year=3, interests=["coding", "hackathons"])
    um.add_user("5", "Emma Sen", username="emma", branch="IT", year=3, interests=["photography", "art"])
    um.add_user("6", "Frank Liu", username="frank", branch="ME", year=1, interests=["cricket", "gaming"])
    um.add_user("7", "Grace Nair", username="grace", branch="ME", year=1, interests=["cricket"])
    um.add_user("8", "Hannah Joy", username="hannah", branch="CE", year=4, interests=["reading"])
    return um


class TestGraphExtensions:
    """Test degree, neighbors, edges(), and connected_components()."""

    def test_degree_and_neighbors(self, sample_campus_graph):
        g = sample_campus_graph
        assert g.degree("1") == 2
        assert g.neighbors("1") == {"2", "3"}
        assert g.degree("8") == 0
        assert g.neighbors("8") == set()
        assert g.degree("nonexistent") == 0
        assert g.neighbors("nonexistent") == set()

    def test_edges(self, sample_campus_graph):
        g = sample_campus_graph
        edges = g.edges()
        assert len(edges) == 6  # 5 in main + 1 in small component
        assert ("1", "2") in edges
        assert ("6", "7") in edges

    def test_connected_components(self, sample_campus_graph):
        g = sample_campus_graph
        components = g.connected_components()
        assert len(components) == 3
        # Sorted by length descending: main (5 nodes), small (2 nodes), isolated (1 node)
        assert len(components[0]) == 5
        assert set(components[0]) == {"1", "2", "3", "4", "5"}
        assert len(components[1]) == 2
        assert set(components[1]) == {"6", "7"}
        assert components[2] == ["8"]


class TestBFSExtensions:
    """Test bfs_levels, bfs_steps, and verify_with_networkx."""

    def test_bfs_levels(self, sample_campus_graph):
        g = sample_campus_graph
        levels = bfs_levels(g, "1")
        # 1's friends: 2, 3 (level 1)
        # 2 and 3 connect to 4 (level 2)
        # 4 connects to 5 (level 3)
        assert levels[1] == ["2", "3"]
        assert levels[2] == ["4"]
        assert levels[3] == ["5"]
        assert 4 not in levels

        # Isolated node has no levels
        assert bfs_levels(g, "8") == {}
        # Invalid node
        assert bfs_levels(g, "999") == {}

    def test_bfs_steps_reach_target(self, sample_campus_graph):
        g = sample_campus_graph
        steps = list(bfs_steps(g, "1", "5"))
        assert len(steps) >= 3
        # Initial step
        assert steps[0]["step"] == 0
        assert steps[0]["found"] is False
        assert "1" in steps[0]["queue"]

        # Final step
        final = steps[-1]
        assert final["found"] is True
        assert final["path"] is not None
        assert final["path"][0] == "1"
        assert final["path"][-1] == "5"

    def test_bfs_steps_disconnected(self, sample_campus_graph):
        g = sample_campus_graph
        steps = list(bfs_steps(g, "1", "6"))
        final = steps[-1]
        assert final["found"] is False
        assert final["path"] is None
        assert "disconnected" in final["message"].lower() or "empty" in final["message"].lower()

    def test_bfs_steps_same_node(self, sample_campus_graph):
        g = sample_campus_graph
        steps = list(bfs_steps(g, "1", "1"))
        assert len(steps) == 1
        assert steps[0]["found"] is True
        assert steps[0]["path"] == ["1"]

    def test_verify_with_networkx(self, sample_campus_graph):
        g = sample_campus_graph
        # Connected pair
        assert verify_with_networkx(g, "1", "5") is True
        # Direct friends
        assert verify_with_networkx(g, "1", "2") is True
        # Same node
        assert verify_with_networkx(g, "1", "1") is True
        # Disconnected pair
        assert verify_with_networkx(g, "1", "6") is True
        assert verify_with_networkx(g, "1", "8") is True


class TestJaccardAndRecommendations:
    """Test Jaccard calculation and hybrid recommendation ranking."""

    def test_calculate_jaccard_similarity(self):
        s1 = {"coding", "music"}
        s2 = {"coding", "gaming"}
        # Intersection = {"coding"} (1), Union = {"coding", "music", "gaming"} (3) -> 1/3 = 0.333
        assert calculate_jaccard_similarity(s1, s2) == 0.333

        # Identical sets
        assert calculate_jaccard_similarity(s1, s1) == 1.0
        # Disjoint sets
        assert calculate_jaccard_similarity(s1, {"art", "dance"}) == 0.0
        # Empty sets
        assert calculate_jaccard_similarity(set(), {"music"}) == 0.0
        assert calculate_jaccard_similarity(set(), set()) == 0.0

    def test_recommendations_with_jaccard_ranking(self, sample_campus_graph, sample_campus_manager):
        g = sample_campus_graph
        um = sample_campus_manager

        recs = get_friend_recommendations(g, "1", user_manager=um)
        # For 1 (Alice), direct friends are 2 and 3.
        # Candidates from 2 (Bob) and 3 (Charlie):
        # 2's friend is 4 (David), 3's friend is 4 (David).
        # David has 2 mutual friends (Bob and Charlie).
        assert len(recs) == 1
        assert recs[0]["user_id"] == "4"
        assert recs[0]["mutual_count"] == 2
        assert recs[0]["shared_interests"] == ["coding"]
        assert recs[0]["jaccard"] > 0
        assert "mutual friends" in recs[0]["score_explanation"]
        assert "shares coding" in recs[0]["score_explanation"]

    def test_recommendations_filters(self, sample_campus_graph, sample_campus_manager):
        g = sample_campus_graph
        um = sample_campus_manager

        # Candidate 4 is CSE, Year 3
        recs_cse = get_friend_recommendations(g, "1", user_manager=um, branch_filter="CSE")
        assert len(recs_cse) == 1

        recs_ece = get_friend_recommendations(g, "1", user_manager=um, branch_filter="ECE")
        assert len(recs_ece) == 0

        recs_year3 = get_friend_recommendations(g, "1", user_manager=um, year_filter=3)
        assert len(recs_year3) == 1

        recs_year1 = get_friend_recommendations(g, "1", user_manager=um, year_filter=1)
        assert len(recs_year1) == 0


class TestUserManagerCampusFeatures:
    """Test username uniqueness, search, display name, and auto ID generation."""

    def test_username_uniqueness(self, sample_campus_manager):
        um = sample_campus_manager
        # Existing username "alice" should be rejected
        assert um.add_user("9", "Alice Two", username="alice") is False
        # Case-insensitive duplicate check
        assert um.add_user("9", "Alice Two", username="ALICE") is False
        # New unique username
        assert um.add_user("9", "Alice Two", username="alice2") is True

    def test_get_user_by_username(self, sample_campus_manager):
        um = sample_campus_manager
        user = um.get_user_by_username("alice")
        assert user is not None
        assert user["name"] == "Alice Roy"
        assert user["id"] == "1"

        # Case-insensitive
        user_caps = um.get_user_by_username("ALICE")
        assert user_caps is not None
        assert user_caps["id"] == "1"

        assert um.get_user_by_username("unknown") is None

    def test_display_name_safety(self, sample_campus_manager):
        um = sample_campus_manager
        assert um.display_name("1") == "Alice Roy"
        assert um.display_name("999") == "User 999"
        assert um.display_name(None) == "Unknown"

    def test_get_next_user_id(self, sample_campus_manager):
        um = sample_campus_manager
        # Highest ID is currently 8
        assert um.get_next_user_id() == "9"
