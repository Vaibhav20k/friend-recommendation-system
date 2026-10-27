"""Data persistence module for loading and saving social network data.

Responsible for:
- Reading user registries and friendship connections from JSON files.
- Serializing current in-memory graph and user states back to JSON files.
- Gracefully handling missing files or corrupted/invalid JSON format.
- Preserving bidirectional friendship consistency during serialization.
"""

import json
import os
import re
from typing import Any, Dict, List, Optional, Set, Tuple

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
            # Prevent accessing restricted system roots on Unix-like environments
            clean_posix = clean_path.replace("\\", "/")
            restricted_roots = ("/etc", "/root", "/boot", "/dev", "/proc", "/sys")
            if any(clean_posix == r or clean_posix.startswith(r + "/") for r in restricted_roots):
                return False

            abs_path = os.path.abspath(clean_path)
            abs_posix = abs_path.replace("\\", "/")
            drive_stripped = re.sub(r"^[a-zA-Z]:", "", abs_posix)
            if any(drive_stripped == r or drive_stripped.startswith(r + "/") for r in restricted_roots):
                return False

            restricted_win = ("c:/windows", "c:/winnt", "\\\\.\\")
            if any(abs_posix.lower().startswith(w) for w in restricted_win):
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
                    username = user.get("username")
                    branch = user.get("branch")
                    year = user.get("year")
                    interests = user.get("interests")
                    user_manager.add_user(
                        uid,
                        name,
                        username=username,
                        branch=branch,
                        year=year,
                        interests=interests,
                    )
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

    @staticmethod
    def validate_network_data(data: Any) -> Tuple[bool, List[str]]:
        """Validate network JSON structure, referential integrity, and uniqueness.

        Validates:
        - Root is a dictionary containing 'users' and 'friendships'.
        - Users list contains dictionaries with valid 'id' and 'name'.
        - No duplicate user IDs or duplicate usernames.
        - Friendships contain 2-element lists of distinct user IDs that exist in the users registry.

        Args:
            data: Parsed JSON data to validate.

        Returns:
            Tuple[bool, List[str]]: (is_valid, list of human-readable error descriptions).
        """
        errors: List[str] = []
        if not isinstance(data, dict):
            return False, ["Root JSON must be an object/dictionary with 'users' and 'friendships' keys."]

        users = data.get("users")
        if not isinstance(users, list):
            errors.append("Missing or invalid 'users' key (must be an array/list).")

        friendships = data.get("friendships")
        if not isinstance(friendships, list):
            errors.append("Missing or invalid 'friendships' key (must be an array/list).")

        if errors:
            return False, errors

        registered_ids: Set[str] = set()
        registered_usernames: Set[str] = set()

        for idx, u in enumerate(users):
            if not isinstance(u, dict):
                errors.append(f"User entry #{idx + 1} must be an object.")
                continue
            uid = str(u.get("id", "")).strip()
            name = str(u.get("name", "")).strip()
            if not uid:
                errors.append(f"User entry #{idx + 1} is missing a valid 'id'.")
            elif uid in registered_ids:
                errors.append(f"Duplicate user ID '{uid}' found in users list.")
            else:
                registered_ids.add(uid)

            if not name:
                errors.append(f"User '{uid}' is missing a 'name'.")

            username = u.get("username")
            if username is not None:
                un_clean = str(username).strip().lower()
                if not un_clean:
                    errors.append(f"User '{uid}' has an empty 'username'.")
                elif un_clean in registered_usernames:
                    errors.append(f"Duplicate username '{un_clean}' found for user '{uid}'.")
                else:
                    registered_usernames.add(un_clean)

        for idx, f in enumerate(friendships):
            if not isinstance(f, (list, tuple)) or len(f) != 2:
                errors.append(f"Friendship entry #{idx + 1} must be a 2-element array.")
                continue
            u, v = str(f[0]).strip(), str(f[1]).strip()
            if not u or not v:
                errors.append(f"Friendship #{idx + 1} has an empty user ID endpoint.")
            elif u == v:
                errors.append(f"Self-friendship disallowed: [{u}, {v}].")
            else:
                if u not in registered_ids:
                    errors.append(f"Friendship refers to unknown user ID '{u}'.")
                if v not in registered_ids:
                    errors.append(f"Friendship refers to unknown user ID '{v}'.")

        return len(errors) == 0, errors

    @staticmethod
    def load_from_string(json_str: str) -> Tuple[UserManager, SocialGraph, List[str]]:
        """Load network from a raw JSON string with validation.

        Args:
            json_str: Raw JSON string content.

        Returns:
            Tuple of (UserManager, SocialGraph, errors_list).
            If validation fails or JSON is invalid, returns empty instances and error messages.
        """
        um = UserManager()
        sg = SocialGraph()

        if not isinstance(json_str, str) or not json_str.strip():
            return um, sg, ["Empty JSON payload provided."]

        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as exc:
            return um, sg, [f"JSON Syntax Error: {str(exc)}"]

        is_valid, errors = DataHandler.validate_network_data(data)
        if not is_valid:
            return um, sg, errors

        for u in data.get("users", []):
            uid = str(u["id"]).strip()
            name = str(u.get("name", f"User {uid}")).strip()
            username = u.get("username")
            branch = u.get("branch")
            year = u.get("year")
            interests = u.get("interests")
            um.add_user(uid, name, username=username, branch=branch, year=year, interests=interests)
            sg.add_user(uid)

        for pair in data.get("friendships", []):
            u, v = str(pair[0]).strip(), str(pair[1]).strip()
            sg.add_friendship(u, v)

        return um, sg, []

    @staticmethod
    def export_to_json_string(user_manager: UserManager, graph: SocialGraph) -> str:
        """Export current user registry and graph state to a formatted JSON string.

        Args:
            user_manager: UserManager instance.
            graph: SocialGraph instance.

        Returns:
            Formatted JSON string suitable for file download.
        """
        users_list = user_manager.get_all_users()
        registered_ids = {u["id"] for u in users_list}

        for uid in graph.get_all_users():
            if uid not in registered_ids:
                users_list.append({"id": uid, "name": f"User {uid}"})
                registered_ids.add(uid)

        def user_sort_key(user: dict) -> Tuple[int, int, str]:
            uid = str(user.get("id", ""))
            return (0, int(uid), uid) if uid.isdigit() else (1, 0, uid)

        users_list.sort(key=user_sort_key)

        seen_edges = set()
        friendships_list = []
        for u, neighbors in graph.get_adjacency_list().items():
            for v in neighbors:
                edge = (min(u, v), max(u, v))
                if edge not in seen_edges:
                    seen_edges.add(edge)
                    friendships_list.append([edge[0], edge[1]])

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
        return json.dumps(payload, indent=2)
