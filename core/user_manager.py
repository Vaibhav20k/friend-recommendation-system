"""User and student profile management module for the CampusConnect network.

Responsible for:
- Maintaining the user/student registry (mapping user ID -> student record).
- Fast O(1) average lookup by user ID, display name, and unique lowercase username.
- Integrating hand-written HashTable for the username -> user_id index.
- Preventing duplicate usernames and duplicate user IDs.
- Substring search and filtering by branch, year, and interests.
- Returning defensive copies of user records to maintain encapsulation.
"""

import re
from typing import Any, Dict, List, Optional
from core.hash_table import HashTable


class UserManager:
    """Manages student identity, profile records, and lookup indices.

    Maintains:
    - `_users`: Maps user_id -> student record dict
    - `_name_to_id`: Maps student display name -> user_id
    - `_username_index`: Custom HashTable mapping username (lowercase) -> user_id
    """

    def __init__(self) -> None:
        """Initialize an empty UserManager."""
        self._users: Dict[str, Dict[str, Any]] = {}
        self._name_to_id: Dict[str, str] = {}
        self._username_index: HashTable = HashTable(initial_capacity=16, max_load_factor=0.75)

    @property
    def username_index(self) -> HashTable:
        """Access the internal hand-written HashTable for hash inspection and benchmarking."""
        return self._username_index

    def add_user(
        self,
        user_id: str,
        name: str,
        username: Optional[str] = None,
        branch: Optional[str] = None,
        year: Optional[int] = None,
        interests: Optional[List[str]] = None,
    ) -> bool:
        """Add a new student user to the registry.

        Time Complexity:
            Average Case: O(1) dictionary and HashTable insertions.

        Args:
            user_id: Unique string identifier for the student.
            name: Display name of the student.
            username: Optional unique lowercase handle. If omitted, derived from name.
            branch: College branch (e.g. CSE, ECE, ME, CE, IT). Default "CSE".
            year: Study year (1 to 4). Default 1.
            interests: List of interest tags (e.g. ["coding", "music"]).

        Returns:
            True if student was successfully registered, False if inputs are invalid,
            user_id already exists, or username is already taken.
        """
        if not isinstance(user_id, str) or not isinstance(name, str):
            return False
        user_id = user_id.strip()
        name = name.strip()
        if not user_id or not name:
            return False
        if user_id in self._users:
            return False

        # Process and validate username
        if username is None:
            base_un = re.sub(r"[^a-zA-Z0-9_]", "", name.lower().replace(" ", "_"))
            if not base_un:
                base_un = f"user_{user_id}"
            un = base_un
            # Auto-disambiguate if default derived username collides
            if un in self._username_index:
                un = f"{base_un}_{user_id}"
        else:
            if not isinstance(username, str):
                return False
            un = username.strip().lower()
            if not un:
                return False
            if un in self._username_index:
                return False  # Reject duplicate username

        record: Dict[str, Any] = {
            "id": user_id,
            "name": name,
        }
        if username is not None:
            record["username"] = un
        if branch is not None:
            record["branch"] = str(branch).strip().upper()
        if year is not None:
            try:
                y = int(year)
                record["year"] = y if 1 <= y <= 4 else 1
            except (ValueError, TypeError):
                record["year"] = 1
        if interests is not None:
            clean_interests: List[str] = []
            if isinstance(interests, (list, tuple, set)):
                for item in interests:
                    if isinstance(item, str) and item.strip():
                        clean_interests.append(item.strip().lower())
            record["interests"] = clean_interests

        self._users[user_id] = record
        self._name_to_id[name] = user_id
        self._username_index.put(un, user_id)
        return True

    def remove_user(self, user_id: str) -> bool:
        """Remove a user from registry and update name and username indices.

        Args:
            user_id: Unique string identifier of the user to remove.

        Returns:
            True if user was found and removed, False otherwise.
        """
        if not isinstance(user_id, str):
            return False
        user_id = user_id.strip()
        user = self._users.pop(user_id, None)
        if user is None:
            return False

        # Clean up name index
        user_name = user.get("name", "")
        if self._name_to_id.get(user_name) == user_id:
            del self._name_to_id[user_name]

        # Clean up username HashTable index
        un = user.get("username", "")
        if un:
            self._username_index.remove(un)

        return True

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a user's record by user ID.

        Returns a defensive copy of the dictionary to prevent external mutation.
        """
        if not isinstance(user_id, str):
            return None
        user = self._users.get(user_id.strip())
        if not user:
            return None
        copy = user.copy()
        if "interests" in user:
            copy["interests"] = list(user["interests"])
        return copy

    def get_user_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Retrieve a user's record by exact or case-insensitive display name."""
        if not isinstance(name, str):
            return None
        name = name.strip()
        if not name:
            return None

        # O(1) fast lookup
        if name in self._name_to_id:
            uid = self._name_to_id[name]
            return self.get_user(uid)

        # Case-insensitive fallback
        name_lower = name.lower()
        for user in self._users.values():
            if user["name"].lower() == name_lower:
                return self.get_user(user["id"])

        return None

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Retrieve a user's record using the custom HashTable username index.

        Time Complexity:
            Average Case: O(1) via custom HashTable.
        """
        if not isinstance(username, str):
            return None
        un = username.strip().lower()
        uid = self._username_index.get(un)
        if uid is not None:
            return self.get_user(uid)
        return None

    def search_users(self, query: str) -> List[Dict[str, Any]]:
        """Search for users whose names or usernames contain the query substring."""
        if not isinstance(query, str):
            return []
        q = query.strip().lower()
        results: List[Dict[str, Any]] = []
        for user in self._users.values():
            if (
                q in user["name"].lower()
                or q in user.get("username", "").lower()
                or any(q in interest.lower() for interest in user.get("interests", []))
            ):
                results.append(self.get_user(user["id"]))  # type: ignore
        return results

    def display_name(self, user_id: str) -> str:
        """Safe display name helper that never crashes even on missing/None user IDs."""
        if user_id is None:
            return "Unknown"
        uid = str(user_id).strip()
        user = self._users.get(uid)
        if user and "name" in user and user["name"]:
            return user["name"]
        return f"User {uid}"

    def get_next_user_id(self) -> str:
        """Auto-generate the next sequential user ID."""
        numeric_ids = []
        for uid in self._users.keys():
            if uid.isdigit():
                numeric_ids.append(int(uid))
        if numeric_ids:
            return str(max(numeric_ids) + 1)
        return str(len(self._users) + 1)

    def get_all_users(self) -> List[Dict[str, Any]]:
        """Return a list containing copies of all registered student records."""
        return [self.get_user(uid) for uid in self._users.keys()]  # type: ignore

    def get_user_count(self) -> int:
        """Return the total number of registered users."""
        return len(self._users)

    def exists(self, user_id: str) -> bool:
        """Check whether a user with the given ID exists in the registry."""
        if not isinstance(user_id, str):
            return False
        return user_id.strip() in self._users

    def clear(self) -> None:
        """Reset the registry, name index, and username HashTable to empty state."""
        self._users.clear()
        self._name_to_id.clear()
        self._username_index.clear()

    def __contains__(self, user_id: str) -> bool:
        """Enable pythonic 'user_id in user_manager' syntax."""
        return self.exists(user_id)

    def __len__(self) -> int:
        """Enable pythonic 'len(user_manager)' returning user count."""
        return self.get_user_count()

    def __repr__(self) -> str:
        """Return a string representation of UserManager."""
        return f"UserManager(users={self.get_user_count()})"


def display_name(user_manager: Optional[UserManager], user_id: str) -> str:
    """Standalone safe helper to get display name for user_id without None crashes."""
    if user_manager is not None:
        return user_manager.display_name(user_id)
    return f"User {user_id}" if user_id is not None else "Unknown"
