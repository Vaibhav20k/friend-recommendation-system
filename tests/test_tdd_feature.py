"""TDD (Test-Driven Development) Demonstration Suite.

Tests created BEFORE implementation following the strict Red -> Green -> Refactor cycle:
1. Feature A: get_network_metrics(graph: SocialGraph) -> Dict[str, Any]
2. Feature B: get_mutual_friends_details(graph: SocialGraph, user_u: str, user_v: str, user_manager=None) -> Dict[str, Any]
"""

import pytest
from core.graph import SocialGraph, get_network_metrics
from core.user_manager import UserManager
from core.recommendation import get_mutual_friends_details


class TestTDDNetworkMetrics:
    """TDD test cases for get_network_metrics."""

    def test_empty_graph_metrics(self):
        """Empty graph should return zeroed metrics without ZeroDivisionError."""
        graph = SocialGraph()
        metrics = get_network_metrics(graph)

        assert metrics["total_users"] == 0
        assert metrics["total_friendships"] == 0
        assert metrics["density"] == 0.0
        assert metrics["average_degree"] == 0.0
        assert metrics["isolated_count"] == 0
        assert metrics["isolated_users"] == []
        assert metrics["max_degree"] == 0
        assert metrics["max_degree_users"] == []
        assert metrics["degrees"] == {}

    def test_single_isolated_user_metrics(self):
        """Graph with 1 user and 0 edges."""
        graph = SocialGraph()
        graph.add_user("1")
        metrics = get_network_metrics(graph)

        assert metrics["total_users"] == 1
        assert metrics["total_friendships"] == 0
        assert metrics["density"] == 0.0
        assert metrics["average_degree"] == 0.0
        assert metrics["isolated_count"] == 1
        assert metrics["isolated_users"] == ["1"]
        assert metrics["max_degree"] == 0
        assert metrics["max_degree_users"] == [("1", 0)]
        assert metrics["degrees"] == {"1": 0}

    def test_triangle_graph_metrics(self):
        """Complete graph K3 (triangle): 3 users, 3 edges, density 1.0, avg degree 2.0."""
        graph = SocialGraph()
        graph.add_friendship("A", "B")
        graph.add_friendship("B", "C")
        graph.add_friendship("A", "C")

        metrics = get_network_metrics(graph)
        assert metrics["total_users"] == 3
        assert metrics["total_friendships"] == 3
        # Density for K3: 2 * 3 / (3 * 2) = 1.0
        assert metrics["density"] == 1.0
        assert metrics["average_degree"] == 2.0
        assert metrics["isolated_count"] == 0
        assert metrics["isolated_users"] == []
        assert metrics["max_degree"] == 2
        assert len(metrics["max_degree_users"]) == 3

    def test_mixed_graph_with_isolates(self):
        """Graph with connected components and an isolated user."""
        graph = SocialGraph()
        # Alice, Bob, Charlie line graph
        graph.add_friendship("1", "2")
        graph.add_friendship("2", "3")
        # Liam isolated
        graph.add_user("12")

        metrics = get_network_metrics(graph)
        assert metrics["total_users"] == 4
        assert metrics["total_friendships"] == 2
        # Max possible edges: 4 * 3 / 2 = 6; Density = 2 / 6 = 0.3333...
        assert round(metrics["density"], 4) == round(2 / 6, 4)
        # Average degree: 2 * 2 / 4 = 1.0
        assert metrics["average_degree"] == 1.0
        assert metrics["isolated_count"] == 1
        assert metrics["isolated_users"] == ["12"]
        assert metrics["max_degree"] == 2
        assert metrics["max_degree_users"] == [("2", 2)]

    def test_social_graph_method_binding(self):
        """SocialGraph instance should also provide .get_network_metrics() method."""
        graph = SocialGraph()
        graph.add_friendship("X", "Y")
        metrics = graph.get_network_metrics()
        assert metrics["total_users"] == 2
        assert metrics["total_friendships"] == 1
        assert metrics["density"] == 1.0


class TestTDDMutualFriendsDetails:
    """TDD test cases for get_mutual_friends_details."""

    def test_mutual_friends_details_without_user_manager(self):
        """Calculates mutual friends between two users without UserManager."""
        graph = SocialGraph()
        # Alice (1) and Emma (5) share Bob (2) and Charlie (3)
        graph.add_friendship("1", "2")
        graph.add_friendship("1", "3")
        graph.add_friendship("5", "2")
        graph.add_friendship("5", "3")

        result = get_mutual_friends_details(graph, "1", "5")
        assert result["user_u"] == "1"
        assert result["user_v"] == "5"
        assert result["are_friends"] is False
        assert result["mutual_count"] == 2
        assert result["mutual_friends"] == ["2", "3"]
        assert result["mutual_friends_detailed"] == [
            {"id": "2", "name": "User 2"},
            {"id": "3", "name": "User 3"},
        ]

    def test_mutual_friends_details_with_user_manager(self):
        """Calculates mutual friends and populates real names from UserManager."""
        graph = SocialGraph()
        um = UserManager()
        um.add_user("1", "Alice")
        um.add_user("2", "Bob")
        um.add_user("3", "Charlie")
        um.add_user("5", "Emma")

        graph.add_friendship("1", "2")
        graph.add_friendship("1", "3")
        graph.add_friendship("5", "2")
        graph.add_friendship("5", "3")

        result = get_mutual_friends_details(graph, "1", "5", user_manager=um)
        assert result["mutual_count"] == 2
        assert result["mutual_friends"] == ["2", "3"]
        assert result["mutual_friends_detailed"] == [
            {"id": "2", "name": "Bob"},
            {"id": "3", "name": "Charlie"},
        ]

    def test_mutual_friends_when_users_are_already_friends(self):
        """When two users are already direct friends, are_friends is True and mutuals are still computed."""
        graph = SocialGraph()
        # Triangle A-B, B-C, A-C
        graph.add_friendship("A", "B")
        graph.add_friendship("B", "C")
        graph.add_friendship("A", "C")

        result = get_mutual_friends_details(graph, "A", "B")
        assert result["are_friends"] is True
        assert result["mutual_count"] == 1
        assert result["mutual_friends"] == ["C"]

    def test_mutual_friends_non_existent_or_invalid_users(self):
        """Handles non-existent or invalid user inputs gracefully."""
        graph = SocialGraph()
        graph.add_user("1")

        result = get_mutual_friends_details(graph, "1", "999")
        assert result["mutual_count"] == 0
        assert result["mutual_friends"] == []
        assert result["are_friends"] is False

        result_empty = get_mutual_friends_details(graph, "", "1")
        assert result_empty["mutual_count"] == 0
        assert result_empty["mutual_friends"] == []
