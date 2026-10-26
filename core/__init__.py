"""Core module for Graph representation, User Management, BFS, and Friend Recommendations."""

from core.graph import SocialGraph
from core.user_manager import UserManager
from core.recommendation import get_friend_recommendations
from core.bfs import find_shortest_connection

__all__ = [
    "SocialGraph",
    "UserManager",
    "get_friend_recommendations",
    "find_shortest_connection",
]
