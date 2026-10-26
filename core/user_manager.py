"""User management module for the social network.

Responsible for:
- Maintaining the user registry (mapping user ID -> user record).
- Fast O(1) average lookup by user ID or user name.
- Case-insensitive substring search for user discovery.
- User addition, removal, and existence verification.
- Ensuring user record encapsulation by returning defensive copies.

Time Complexities (Average Case):
- add_user: O(1) dictionary insertion
- remove_user: O(1) dictionary deletion
- get_user: O(1) dictionary lookup
- get_user_by_name: O(1) index lookup (with O(N) case-insensitive fallback)
- search_users: O(N * L) linear scan where N is user count and L is string length
- get_all_users: O(N) list creation
- get_user_count: O(1) len(dict) lookup
- exists: O(1) dictionary membership test
- clear: O(1) dictionary reset
"""

from typing import Dict, List, Optional


class UserManager:
    """Manages user identity, profile records, and lookup indices.

    Maintains two primary internal structures:
    - `_users`: Maps user_id -> {"id": str, "name": str}
    - `_name_to_id`: Maps user name -> user_id for fast O(1) lookups by name.
    """

    def __init__(self) -> None:
        """Initialize an empty UserManager."""
        self._users: Dict[str, Dict[str, str]] = {}
        self._name_to_id: Dict[str, str] = {}

    def add_user(self, user_id: str, name: str) -> bool:
        """Add a new user to the registry.

        Time Complexity:
            Average Case: O(1) dictionary insertions.

        Args:
            user_id: Unique string identifier for the user.
            name: Display name of the user.

        Returns:
            True if user was successfully added, False if user_id is empty,
            name is empty, or user_id already exists in the registry.
        """
        if not isinstance(user_id, str) or not isinstance(name, str):
            return False
        user_id = user_id.strip()
        name = name.strip()
        if not user_id or not name:
            return False
        if user_id in self._users:
            return False

        self._users[user_id] = {"id": user_id, "name": name}
        self._name_to_id[name] = user_id
        return True

    def remove_user(self, user_id: str) -> bool:
        """Remove a user from the registry and update the name index.

        Time Complexity:
            Average Case: O(1) dictionary removals.

        Args:
            user_id: Unique string identifier for the user to remove.

        Returns:
            True if the user was found and removed, False otherwise.
        """
        if not isinstance(user_id, str):
            return False
        user_id = user_id.strip()
        user = self._users.pop(user_id, None)
        if user is None:
            return False

        # Clean up name index if it points to this user
        user_name = user.get("name", "")
        if self._name_to_id.get(user_name) == user_id:
            del self._name_to_id[user_name]

        return True

    def get_user(self, user_id: str) -> Optional[Dict[str, str]]:
        """Retrieve a user's record by user ID.

        Returns a defensive copy of the user dictionary to prevent external mutation.

        Time Complexity:
            Average Case: O(1) dictionary lookup.

        Args:
            user_id: String identifier for the user.

        Returns:
            Dictionary with keys {"id": str, "name": str} if found, None otherwise.
        """
        if not isinstance(user_id, str):
            return None
        user = self._users.get(user_id.strip())
        return user.copy() if user else None

    def get_user_by_name(self, name: str) -> Optional[Dict[str, str]]:
        """Retrieve a user's record by exact or case-insensitive name.

        Performs an O(1) lookup on the direct name index first. If not found,
        performs a case-insensitive match over all registered users.

        Time Complexity:
            Average Case: O(1) if exact match hits index, O(N) worst case.

        Args:
            name: Name of the user to look up.

        Returns:
            Dictionary with keys {"id": str, "name": str} if found, None otherwise.
        """
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
                return user.copy()

        return None

    def search_users(self, query: str) -> List[Dict[str, str]]:
        """Search for users whose names contain the given query string.

        Performs a case-insensitive substring search across all registered users.

        Time Complexity:
            O(N * L) where N is the total number of users and L is the average
            length of user names.

        Args:
            query: Substring to search for. If empty, matches all users.

        Returns:
            List of matching user dictionaries {"id": str, "name": str}.
        """
        if not isinstance(query, str):
            return []
        q = query.strip().lower()
        return [
            user.copy()
            for user in self._users.values()
            if q in user["name"].lower()
        ]

    def get_all_users(self) -> List[Dict[str, str]]:
        """Return a list containing copies of all registered user records.

        Time Complexity:
            O(N) where N is the number of registered users.

        Returns:
            List of user dictionaries {"id": str, "name": str}.
        """
        return [user.copy() for user in self._users.values()]

    def get_user_count(self) -> int:
        """Return the total number of registered users.

        Time Complexity:
            O(1) dictionary length lookup.

        Returns:
            Total user count.
        """
        return len(self._users)

    def exists(self, user_id: str) -> bool:
        """Check whether a user with the given ID exists in the registry.

        Time Complexity:
            Average Case: O(1) dictionary key lookup.

        Args:
            user_id: Unique string identifier of the user.

        Returns:
            True if user exists, False otherwise.
        """
        if not isinstance(user_id, str):
            return False
        return user_id.strip() in self._users

    def clear(self) -> None:
        """Reset the registry and name index to an empty state.

        Time Complexity:
            O(1) dictionary clear.
        """
        self._users.clear()
        self._name_to_id.clear()

    def __contains__(self, user_id: str) -> bool:
        """Enable pythonic 'user_id in user_manager' syntax."""
        return self.exists(user_id)

    def __len__(self) -> int:
        """Enable pythonic 'len(user_manager)' returning user count."""
        return self.get_user_count()

    def __repr__(self) -> str:
        """Return a string representation of UserManager."""
        return f"UserManager(users={self.get_user_count()})"
