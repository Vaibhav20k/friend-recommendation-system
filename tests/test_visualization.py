"""Unit tests for graph visualization module (Phase 6)."""

import pytest
import matplotlib.figure
from core.graph import SocialGraph
from core.user_manager import UserManager
from visualization.graph_visualizer import render_social_graph


@pytest.fixture
def sample_network():
    """Create a sample network for testing visualization."""
    um = UserManager()
    sg = SocialGraph()

    for uid, name in [
        ("1", "Alice"),
        ("2", "Bob"),
        ("3", "Charlie"),
        ("4", "David"),
        ("5", "Emma"),
        ("6", "Frank"),
        ("7", "Grace"),
        ("12", "Liam"),
    ]:
        um.add_user(uid, name)
        sg.add_user(uid)

    friendships = [
        ("1", "2"),
        ("1", "3"),
        ("1", "4"),
        ("2", "5"),
        ("2", "6"),
        ("3", "5"),
        ("3", "7"),
        ("4", "6"),
    ]
    for u, v in friendships:
        sg.add_friendship(u, v)

    return um, sg


def test_render_social_graph_returns_figure(sample_network):
    """Test that render_social_graph returns a matplotlib Figure object."""
    um, sg = sample_network
    fig = render_social_graph(sg, um)
    assert isinstance(fig, matplotlib.figure.Figure)


def test_render_social_graph_with_selected_user(sample_network):
    """Test rendering with a selected user."""
    um, sg = sample_network
    fig = render_social_graph(sg, um, selected_user="1")
    assert isinstance(fig, matplotlib.figure.Figure)


def test_render_social_graph_with_recommendations(sample_network):
    """Test rendering with recommended users highlighted."""
    um, sg = sample_network
    fig = render_social_graph(
        sg, um, selected_user="1", recommended_users=["5", "6"]
    )
    assert isinstance(fig, matplotlib.figure.Figure)


def test_render_social_graph_with_path_nodes(sample_network):
    """Test rendering with a BFS shortest path highlighted."""
    um, sg = sample_network
    path = ["1", "3", "7"]
    fig = render_social_graph(
        sg, um, selected_user="1", path_nodes=path
    )
    assert isinstance(fig, matplotlib.figure.Figure)


def test_render_social_graph_empty_graph():
    """Test rendering an empty graph without crashing."""
    um = UserManager()
    sg = SocialGraph()
    fig = render_social_graph(sg, um)
    assert isinstance(fig, matplotlib.figure.Figure)
