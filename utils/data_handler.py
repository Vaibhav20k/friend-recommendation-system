"""Data persistence module for loading and saving social network data.

Responsible for:
- Reading user registries and friendship connections from JSON files.
- Serializing current in-memory graph and user states back to JSON files.
- Gracefully handling missing files or corrupted/invalid JSON format.
- Preserving bidirectional friendship consistency during serialization.
"""

import json
import os
from typing import Optional, Tuple

from core.graph import SocialGraph
from core.user_manager import UserManager


class DataHandler:
    """Handles JSON serialization and deserialization for the social network."""

    @staticmethod
    def is_safe_filepath(filepath: str, allowed_base_dir: Optional[str] = None) -> bool:
        """Validate filepath against path traversal, null bytes, and sensitive system locations.

        Args:
            filepath: Target file path to check.
            allowed_base_dir: Optional directory to constrain paths within.

        Returns:
            True if path is safe to access, False otherwise.
        """
        if not isinstance(filepath, str):
            return False
        clean_path = filepath.strip()
        if not clean_path or "\0" in clean_path:
            return False

        try:
            abs_path = os.path.abspath(clean_path)
            # Prevent accessing restricted system roots on Unix-like environments
            restricted_roots = ("/etc", "/root", "/boot", "/dev", "/proc", "/sys")
            if any(abs_path == r or abs_path.startswith(r + "/") for r in restricted_roots):
                return False

            if allowed_base_dir is not None:
                abs_base = os.path.abspath(allowed_base_dir)
                common = os.path.commonpath([abs_base, abs_path])
                if common != abs_base:
                    return False

            return True
        except Exception:
            return False

    @staticmethod
    def load_network(
        filepath: str, allowed_base_dir: Optional[str] = None
    ) -> Tuple[UserManager, SocialGraph]:
        """Load user accounts and friendships from a JSON file into memory.

        Expected JSON format:
        {
            "users": [
                {"id": "1", "name": "Alice"},
                ...
            ],
            "friendships": [
                ["1", "2"],
                ...
            ]
        }

        Handles `FileNotFoundError` and `json.JSONDecodeError` gracefully by
        returning fresh, empty instances of `UserManager` and `SocialGraph`.

        Args:
            filepath: Path to the JSON file to load.
            allowed_base_dir: Optional directory to restrict file access to.

        Returns:
            A tuple containing (UserManager, SocialGraph) populated from file.
        """
        user_manager = UserManager()
        social_graph = SocialGraph()

        if not DataHandler.is_safe_filepath(filepath, allowed_base_dir):
            return user_manager, social_graph

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return user_manager, social_graph
        except Exception:
            return user_manager, social_graph

        if not isinstance(data, dict):
            return user_manager, social_graph

        # Populate users
        users = data.get("users", [])
        if isinstance(users, list):
            for user in users:
                if isinstance(user, dict) and "id" in user:
                    uid = str(user["id"]).strip()
                    if not uid:
                        continue
                    raw_name = str(user.get("name", "")).strip()
                    name = raw_name if raw_name else f"User {uid}"
                    user_manager.add_user(uid, name)
                    social_graph.add_user(uid)

        # Populate friendships
        friendships = data.get("friendships", [])
        if isinstance(friendships, list):
            for pair in friendships:
                if isinstance(pair, (list, tuple)) and len(pair) == 2:
                    if pair[0] is None or pair[1] is None:
                        continue
                    u, v = str(pair[0]).strip(), str(pair[1]).strip()
                    if not u or not v or u == v:
                        continue
                    social_graph.add_friendship(u, v)
                    # If any endpoint wasn't in users list, ensure UserManager has record
                    if not user_manager.exists(u):
                        user_manager.add_user(u, f"User {u}")
                    if not user_manager.exists(v):
                        user_manager.add_user(v, f"User {v}")

        return user_manager, social_graph

    @staticmethod
    def save_network(
        user_manager: UserManager,
        graph: SocialGraph,
        filepath: str,
        allowed_base_dir: Optional[str] = None,
    ) -> bool:
        """Save user registry and friendships to a nicely formatted JSON file.

        Dumps all users from the user registry and all unique undirected
        friendships from the graph into JSON with indentation.

        Args:
            user_manager: UserManager instance holding user records.
            graph: SocialGraph instance holding friendship edges.
            filepath: Destination file path for the JSON dump.
            allowed_base_dir: Optional directory to restrict file saving to.

        Returns:
            True if saving succeeded, False if any I/O or serialization error occurred.
        """
        if not DataHandler.is_safe_filepath(filepath, allowed_base_dir):
            return False

        try:
            # Ensure target parent directory exists
            dirname = os.path.dirname(os.path.abspath(filepath))
            if dirname:
                os.makedirs(dirname, exist_ok=True)

            # Collect all users
            users_list = user_manager.get_all_users()
            registered_ids = {u["id"] for u in users_list}

            # If there are users in graph not in user_manager, include them
            for uid in graph.get_all_users():
                if uid not in registered_ids:
                    users_list.append({"id": uid, "name": f"User {uid}"})
                    registered_ids.add(uid)

            # Sort users deterministically (numerically if numeric string, else lexicographically)
            def user_sort_key(user: dict) -> Tuple[int, int, str]:
                uid = str(user.get("id", ""))
                if uid.isdigit():
                    return (0, int(uid), uid)
                return (1, 0, uid)

            users_list.sort(key=user_sort_key)

            # Collect unique undirected friendships
            seen_edges = set()
            friendships_list = []
            for u, neighbors in graph.get_adjacency_list().items():
                for v in neighbors:
                    edge = (min(u, v), max(u, v))
                    if edge not in seen_edges:
                        seen_edges.add(edge)
                        friendships_list.append([edge[0], edge[1]])

            # Sort friendships deterministically
            def edge_sort_key(edge: list) -> Tuple[int, int, str, int, int, str]:
                u, v = str(edge[0]), str(edge[1])
                u_key = (0, int(u), u) if u.isdigit() else (1, 0, u)
                v_key = (0, int(v), v) if v.isdigit() else (1, 0, v)
                return u_key + v_key

            friendships_list.sort(key=edge_sort_key)

            payload = {
                "users": users_list,
                "friendships": friendships_list,
            }

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)

            return True
        except Exception:
            return False
