"""Unit tests for mutual friend calculation and candidate ranking (Phase 3)."""

import pytest
from core.graph import SocialGraph
from core.recommendation import get_friend_recommendations


@pytest.fixture
def sample_social_graph() -> SocialGraph:
    r"""Fixture to build the standard social network graph.

    Graph topology:
        Alice (1)   --- Bob (2)   --- Emma (5)
          |     \         |
          |       \       |
        Charlie (3) --- David (4) --- Frank (6)
          |
        Grace (7)

        Liam (12) [Isolated node with no friendships]
    """
    graph = SocialGraph()
    # Add all users
    for user_id in ["1", "2", "3", "4", "5", "6", "7", "12"]:
        graph.add_user(user_id)

    # Establish friendships
    friendships = [
        ("1", "2"),  # Alice - Bob
        ("1", "3"),  # Alice - Charlie
        ("1", "4"),  # Alice - David
        ("2", "5"),  # Bob - Emma
        ("2", "6"),  # Bob - Frank
        ("3", "5"),  # Charlie - Emma
        ("3", "7"),  # Charlie - Grace
        ("4", "6"),  # David - Frank
    ]
    for u1, u2 in friendships:
        graph.add_friendship(u1, u2)

    return graph


def test_recommendations_for_alice(sample_social_graph: SocialGraph):
    """Test recommendations for Alice:

    Emma and Frank should have 2 mutual friends, Grace 1 mutual friend.
    Candidates should be ranked descending by mutual count and tie-broken alphabetically.
    """
    recommendations = get_friend_recommendations(sample_social_graph, "1")

    assert len(recommendations) == 3

    # Rank 1: Emma (5) with 2 mutual friends (Bob: 2, Charlie: 3)
    assert recommendations[0]["user_id"] == "5"
    assert recommendations[0]["mutual_count"] == 2
    assert recommendations[0]["mutual_friends"] == ["2", "3"]

    # Rank 2: Frank (6) with 2 mutual friends (Bob: 2, David: 4)
    assert recommendations[1]["user_id"] == "6"
    assert recommendations[1]["mutual_count"] == 2
    assert recommendations[1]["mutual_friends"] == ["2", "4"]

    # Rank 3: Grace (7) with 1 mutual friend (Charlie: 3)
    assert recommendations[2]["user_id"] == "7"
    assert recommendations[2]["mutual_count"] == 1
    assert recommendations[2]["mutual_friends"] == ["3"]


def test_direct_friends_excluded(sample_social_graph: SocialGraph):
    """Test that direct friends (Bob, Charlie, David) are strictly excluded from recommendations."""
    recommendations = get_friend_recommendations(sample_social_graph, "1")
    recommended_ids = {r["user_id"] for r in recommendations}

    # Direct friends of Alice are '2', '3', '4'
    assert "2" not in recommended_ids
    assert "3" not in recommended_ids
    assert "4" not in recommended_ids


def test_self_excluded(sample_social_graph: SocialGraph):
    """Test that the query user (Alice herself) is excluded from candidate recommendations."""
    recommendations = get_friend_recommendations(sample_social_graph, "1")
    recommended_ids = {r["user_id"] for r in recommendations}

    assert "1" not in recommended_ids


def test_user_with_no_friends(sample_social_graph: SocialGraph):
    """Test that a user with no friends (Liam: 12) returns an empty list []."""
    recommendations = get_friend_recommendations(sample_social_graph, "12")
    assert recommendations == []


def test_all_friends_of_friends_are_direct_friends():
    """Test a scenario where all friends-of-friends are already direct friends (complete triangle)."""
    triangle_graph = SocialGraph()
    # K3 complete graph: A - B, B - C, A - C
    triangle_graph.add_friendship("A", "B")
    triangle_graph.add_friendship("B", "C")
    triangle_graph.add_friendship("A", "C")

    # For user A, direct friends are B and C.
    # B's friends are A and C (A is self, C is direct friend).
    # C's friends are A and B (A is self, B is direct friend).
    # Thus, no unacquainted candidate exists.
    assert get_friend_recommendations(triangle_graph, "A") == []
    assert get_friend_recommendations(triangle_graph, "B") == []
    assert get_friend_recommendations(triangle_graph, "C") == []


def test_non_existent_user(sample_social_graph: SocialGraph):
    """Test that querying a non-existent user returns an empty list []."""
    assert get_friend_recommendations(sample_social_graph, "999") == []
    assert get_friend_recommendations(sample_social_graph, "unknown_user") == []
    assert get_friend_recommendations(sample_social_graph, "") == []


def test_recommendations_with_limit(sample_social_graph: SocialGraph):
    """Test recommendation limiting functionality."""
    # Alice has 3 total candidate recommendations: Emma (5), Frank (6), Grace (7)
    top_1 = get_friend_recommendations(sample_social_graph, "1", limit=1)
    assert len(top_1) == 1
    assert top_1[0]["user_id"] == "5"

    top_2 = get_friend_recommendations(sample_social_graph, "1", limit=2)
    assert len(top_2) == 2
    assert top_2[0]["user_id"] == "5"
    assert top_2[1]["user_id"] == "6"

    # Limit larger than total candidate count returns all candidates
    top_10 = get_friend_recommendations(sample_social_graph, "1", limit=10)
    assert len(top_10) == 3

    # Limit <= 0 returns empty list
    top_0 = get_friend_recommendations(sample_social_graph, "1", limit=0)
    assert top_0 == []
    top_neg = get_friend_recommendations(sample_social_graph, "1", limit=-1)
    assert top_neg == []


def test_tie_breaking_alphabetical_order():
    """Verify that candidate users with equal mutual counts are ordered alphabetically."""
    graph = SocialGraph()
    # Hub user H is friends with F1 and F2
    graph.add_friendship("H", "F1")
    graph.add_friendship("H", "F2")

    # Both candidate "Zebra" and candidate "Alpha" are friends with F1 and F2
    graph.add_friendship("Alpha", "F1")
    graph.add_friendship("Alpha", "F2")
    graph.add_friendship("Zebra", "F1")
    graph.add_friendship("Zebra", "F2")

    recs = get_friend_recommendations(graph, "H")
    assert len(recs) == 2
    assert recs[0]["user_id"] == "Alpha"
    assert recs[0]["mutual_count"] == 2
    assert recs[1]["user_id"] == "Zebra"
    assert recs[1]["mutual_count"] == 2


def test_recommendation_empty_graph():
    """Empty graph returns empty recommendations list."""
    empty_graph = SocialGraph()
    assert get_friend_recommendations(empty_graph, "1") == []


def test_recommendation_single_node_graph():
    """Single node graph has no friends, returning empty list."""
    graph = SocialGraph()
    graph.add_user("solo")
    assert get_friend_recommendations(graph, "solo") == []


def test_recommendation_direct_friends_with_no_secondary_connections():
    """User has direct friends, but those direct friends have no other friends."""
    graph = SocialGraph()
    # User 1 is friends with 2 and 3, but neither 2 nor 3 has any other friends
    graph.add_friendship("1", "2")
    graph.add_friendship("1", "3")

    recs = get_friend_recommendations(graph, "1")
    assert recs == []


def test_recommendation_limit_type_and_boundary_safety(sample_social_graph: SocialGraph):
    """Testing invalid or boundary limit arguments."""
    # Non-integer limits (strings, floats, bools) should be rejected safely
    assert get_friend_recommendations(sample_social_graph, "1", limit="2") == []  # type: ignore
    assert get_friend_recommendations(sample_social_graph, "1", limit=1.5) == []  # type: ignore
    assert get_friend_recommendations(sample_social_graph, "1", limit=True) == []  # type: ignore
    assert get_friend_recommendations(sample_social_graph, "1", limit=False) == []  # type: ignore

    # Exact limit equal to total recommendation count (3)
    exact_recs = get_friend_recommendations(sample_social_graph, "1", limit=3)
    assert len(exact_recs) == 3


def test_recommendation_type_safety():
    """Testing invalid types for user_id."""
    graph = SocialGraph()
    graph.add_friendship("1", "2")
    assert get_friend_recommendations(graph, None) == []  # type: ignore
    assert get_friend_recommendations(graph, 123) == []  # type: ignore
    assert get_friend_recommendations(graph, ["1"]) == []  # type: ignore
    assert get_friend_recommendations(graph, "   ") == []

