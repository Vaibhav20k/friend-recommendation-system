"""Comprehensive unit tests for SocialGraph, UserManager, and DataHandler.

Validates:
- Graph construction, node additions, node removals, and degree calculations.
- Edge additions, undirected symmetry, auto-node creation, and edge removals.
- Self-friendship rejection and duplicate edge rejection.
- Friendship count accuracy (Handshaking Lemma).
- Encapsulation (returned sets and dicts are defensive copies).
- UserManager CRUD operations, O(1) lookups, and case-insensitive search.
- DataHandler JSON loading, persistence, error handling, and round-trip fidelity.
"""

import json
import os
import pytest

from core.graph import SocialGraph
from core.user_manager import UserManager
from utils.data_handler import DataHandler


class TestSocialGraph:
    """Unit tests for the SocialGraph class."""

    def test_init_empty_graph(self):
        """Newly created graph should be empty."""
        graph = SocialGraph()
        assert graph.get_user_count() == 0
        assert graph.get_friendship_count() == 0
        assert graph.get_all_users() == set()
        assert graph.get_adjacency_list() == {}
        assert len(graph) == 0

    def test_add_user(self):
        """Adding a new user should return True; duplicate or invalid IDs return False."""
        graph = SocialGraph()
        assert graph.add_user("1") is True
        assert graph.has_user("1") is True
        assert "1" in graph
        assert graph.get_user_count() == 1

        # Duplicate addition
        assert graph.add_user("1") is False
        assert graph.get_user_count() == 1

        # Invalid additions
        assert graph.add_user("") is False
        assert graph.add_user(None) is False  # type: ignore

    def test_remove_user_isolated(self):
        """Removing an isolated user should return True and decrement user count."""
        graph = SocialGraph()
        graph.add_user("1")
        assert graph.remove_user("1") is True
        assert graph.has_user("1") is False
        assert graph.get_user_count() == 0

        # Removing again / non-existent user
        assert graph.remove_user("1") is False
        assert graph.remove_user("999") is False

    def test_remove_user_with_friends(self):
        """Removing a user should remove them from all neighbors' friendship sets."""
        graph = SocialGraph()
        graph.add_friendship("1", "2")
        graph.add_friendship("1", "3")
        graph.add_friendship("2", "3")

        assert graph.get_user_count() == 3
        assert graph.get_friendship_count() == 3

        # Remove user "1" who is friends with "2" and "3"
        assert graph.remove_user("1") is True
        assert graph.has_user("1") is False
        assert graph.get_user_count() == 2

        # User 1 should be gone from friends of 2 and 3
        assert graph.get_friends("2") == {"3"}
        assert graph.get_friends("3") == {"2"}
        assert graph.are_friends("1", "2") is False
        assert graph.are_friends("2", "1") is False

        # Only friendship between 2 and 3 remains
        assert graph.get_friendship_count() == 1

    def test_add_friendship_success(self):
        """Adding a friendship creates an undirected edge between two users."""
        graph = SocialGraph()
        # Should automatically add users if not present
        assert graph.add_friendship("1", "2") is True

        assert graph.has_user("1") is True
        assert graph.has_user("2") is True
        assert graph.are_friends("1", "2") is True
        assert graph.are_friends("2", "1") is True
        assert graph.get_friends("1") == {"2"}
        assert graph.get_friends("2") == {"1"}
        assert graph.get_friendship_count() == 1

    def test_add_friendship_self_loop_rejection(self):
        """Self-friendships (u == v) must be rejected."""
        graph = SocialGraph()
        graph.add_user("1")

        assert graph.add_friendship("1", "1") is False
        assert graph.get_friends("1") == set()
        assert graph.get_friendship_count() == 0
        assert graph.are_friends("1", "1") is False

    def test_add_friendship_invalid_users_rejection(self):
        """Empty or invalid user IDs must be rejected."""
        graph = SocialGraph()
        assert graph.add_friendship("", "2") is False
        assert graph.add_friendship("1", "") is False
        assert graph.add_friendship("", "") is False
        assert graph.get_user_count() == 0

    def test_duplicate_friendship_rejection(self):
        """Adding an existing friendship in either direction should return False."""
        graph = SocialGraph()
        assert graph.add_friendship("1", "2") is True

        # Duplicate in forward direction
        assert graph.add_friendship("1", "2") is False
        # Duplicate in reverse direction
        assert graph.add_friendship("2", "1") is False

        assert graph.get_friendship_count() == 1
        assert graph.get_friends("1") == {"2"}

    def test_remove_friendship(self):
        """Removing an existing friendship removes the edge bidirectionally."""
        graph = SocialGraph()
        graph.add_friendship("1", "2")
        graph.add_friendship("2", "3")

        assert graph.get_friendship_count() == 2
        assert graph.remove_friendship("1", "2") is True

        assert graph.are_friends("1", "2") is False
        assert graph.are_friends("2", "1") is False
        assert graph.get_friends("1") == set()
        assert graph.get_friends("2") == {"3"}
        assert graph.get_friendship_count() == 1

        # Non-existent friendship
        assert graph.remove_friendship("1", "2") is False
        assert graph.remove_friendship("1", "99") is False
        assert graph.remove_friendship("88", "99") is False

    def test_get_friends_copy_isolation(self):
        """get_friends should return a defensive copy that does not mutate graph state."""
        graph = SocialGraph()
        graph.add_friendship("1", "2")

        friends = graph.get_friends("1")
        assert friends == {"2"}
        friends.add("99")  # Mutate returned set

        # Internal state should remain unchanged
        assert graph.get_friends("1") == {"2"}
        assert not graph.are_friends("1", "99")

    def test_get_friends_non_existent(self):
        """get_friends on a non-existent user should return an empty set."""
        graph = SocialGraph()
        assert graph.get_friends("unknown") == set()

    def test_get_all_users(self):
        """get_all_users should return set of all registered user IDs."""
        graph = SocialGraph()
        graph.add_user("A")
        graph.add_user("B")
        graph.add_user("C")

        assert graph.get_all_users() == {"A", "B", "C"}
        assert graph.get_user_count() == 3

    def test_get_adjacency_list_isolation(self):
        """get_adjacency_list returns a copy; mutating it does not affect internal state."""
        graph = SocialGraph()
        graph.add_friendship("A", "B")

        adj = graph.get_adjacency_list()
        assert adj == {"A": {"B"}, "B": {"A"}}

        # Mutate the copy
        adj["A"].add("C")
        adj["Z"] = set()

        # Verify internal graph wasn't modified
        assert graph.get_adjacency_list() == {"A": {"B"}, "B": {"A"}}
        assert graph.has_user("Z") is False

    def test_clear_graph(self):
        """clear() should reset graph nodes and edges to empty state."""
        graph = SocialGraph()
        graph.add_friendship("1", "2")
        graph.add_friendship("2", "3")
        graph.add_user("4")

        assert graph.get_user_count() == 4
        assert graph.get_friendship_count() == 2

        graph.clear()
        assert graph.get_user_count() == 0
        assert graph.get_friendship_count() == 0
        assert graph.get_all_users() == set()
        assert graph.get_adjacency_list() == {}

    def test_friendship_count_accuracy(self):
        """Verify friendship count conforms to sum of degrees // 2 under dynamic operations."""
        graph = SocialGraph()
        # Triangle graph: 3 nodes, 3 edges
        graph.add_friendship("1", "2")
        graph.add_friendship("2", "3")
        graph.add_friendship("3", "1")
        assert graph.get_friendship_count() == 3

        # Add isolated node: degree 0, count remains 3
        graph.add_user("4")
        assert graph.get_friendship_count() == 3

        # Connect 4 to 1 and 2: now 5 edges
        graph.add_friendship("4", "1")
        graph.add_friendship("4", "2")
        assert graph.get_friendship_count() == 5

        # Remove 4: 2 edges removed, 3 edges remain
        graph.remove_user("4")
        assert graph.get_friendship_count() == 3

        # Remove friendship between 1 and 2: 2 edges remain
        graph.remove_friendship("1", "2")
        assert graph.get_friendship_count() == 2

    def test_sample_network_topology(self):
        """Verify the 12-user sample network topology described in README."""
        graph = SocialGraph()
        # Add 12 users
        for i in range(1, 13):
            graph.add_user(str(i))

        # Add 15 edges from specification
        edges = [
            ("1", "2"), ("1", "3"), ("1", "4"),
            ("2", "5"), ("2", "6"),
            ("3", "5"), ("3", "7"),
            ("4", "6"),
            ("5", "8"),
            ("6", "10"),
            ("7", "8"), ("7", "9"),
            ("8", "9"),
            ("9", "11"),
            ("10", "11")
        ]
        for u, v in edges:
            assert graph.add_friendship(u, v) is True

        assert graph.get_user_count() == 12
        assert graph.get_friendship_count() == 15

        # Alice ("1")'s direct friends: Bob ("2"), Charlie ("3"), David ("4")
        assert graph.get_friends("1") == {"2", "3", "4"}

        # Liam ("12") is isolated
        assert graph.get_friends("12") == set()

        # Kelly ("11")'s friends: Ian ("9"), Jack ("10")
        assert graph.get_friends("11") == {"9", "10"}

    def test_repr(self):
        """repr should display user count and friendship count."""
        graph = SocialGraph()
        graph.add_friendship("1", "2")
        assert "users=2" in repr(graph)
        assert "friendships=1" in repr(graph)

    def test_empty_graph_boundaries(self):
        """Boundary tests for an empty SocialGraph."""
        graph = SocialGraph()
        assert graph.get_user_count() == 0
        assert graph.get_friendship_count() == 0
        assert graph.has_user("any") is False
        assert graph.are_friends("u", "v") is False
        assert graph.get_friends("any") == set()
        assert graph.remove_user("any") is False
        assert graph.remove_friendship("u", "v") is False
        assert graph.get_all_users() == set()
        assert graph.get_adjacency_list() == {}

    def test_single_node_graph_boundaries(self):
        """Boundary tests for a single-node SocialGraph."""
        graph = SocialGraph()
        assert graph.add_user("solo") is True
        assert graph.get_user_count() == 1
        assert graph.get_friendship_count() == 0
        assert graph.get_friends("solo") == set()
        assert graph.are_friends("solo", "solo") is False
        assert graph.add_friendship("solo", "solo") is False
        assert graph.remove_user("solo") is True
        assert graph.get_user_count() == 0
        assert graph.has_user("solo") is False

    def test_type_safety_and_whitespace_rejection(self):
        """Type safety and whitespace input validation for graph operations."""
        graph = SocialGraph()
        # Non-string rejection
        assert graph.add_user(123) is False  # type: ignore
        assert graph.add_user(["user"]) is False  # type: ignore
        assert graph.add_user({"id": "1"}) is False  # type: ignore
        assert graph.add_user(None) is False  # type: ignore
        # Whitespace-only string rejection
        assert graph.add_user("   ") is False
        assert graph.add_user("\t\n") is False
        assert graph.get_user_count() == 0

        # Friendship non-string and whitespace rejection
        assert graph.add_friendship(123, "2") is False  # type: ignore
        assert graph.add_friendship("1", 456) is False  # type: ignore
        assert graph.add_friendship("   ", "2") is False
        assert graph.add_friendship("1", "   ") is False
        assert graph.add_friendship(" 1 ", "1") is False  # Collapses to self-loop after stripping

        # Lookup methods with invalid types
        assert graph.has_user(123) is False  # type: ignore
        assert graph.has_user(None) is False  # type: ignore
        assert graph.get_friends(123) == set()  # type: ignore
        assert graph.are_friends(123, 456) is False  # type: ignore

    def test_complete_graph_k5_properties(self):
        """Complete graph K5 has 5 vertices and 10 edges (5 * 4 / 2)."""
        graph = SocialGraph()
        nodes = ["A", "B", "C", "D", "E"]
        for u in nodes:
            graph.add_user(u)

        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                graph.add_friendship(nodes[i], nodes[j])

        assert graph.get_user_count() == 5
        assert graph.get_friendship_count() == 10
        for u in nodes:
            assert len(graph.get_friends(u)) == 4

    def test_disconnected_multiple_components(self):
        """Graph with multiple disconnected clusters."""
        graph = SocialGraph()
        # Cluster 1: C1_A - C1_B
        graph.add_friendship("C1_A", "C1_B")
        # Cluster 2: C2_A - C2_B - C2_C
        graph.add_friendship("C2_A", "C2_B")
        graph.add_friendship("C2_B", "C2_C")
        # Isolated node: ISO
        graph.add_user("ISO")

        assert graph.get_user_count() == 6
        assert graph.get_friendship_count() == 3
        assert graph.are_friends("C1_A", "C2_A") is False
        assert graph.get_friends("ISO") == set()



class TestUserManager:
    """Unit tests for the UserManager class."""

    def test_init_empty_registry(self):
        """Newly created UserManager should be empty."""
        manager = UserManager()
        assert manager.get_user_count() == 0
        assert manager.get_all_users() == []
        assert len(manager) == 0

    def test_add_user(self):
        """Adding a new user should store their id and name; reject duplicates."""
        manager = UserManager()
        assert manager.add_user("1", "Alice") is True
        assert manager.exists("1") is True
        assert "1" in manager
        assert manager.get_user_count() == 1

        # Duplicate ID rejection
        assert manager.add_user("1", "Alice Clone") is False
        assert manager.get_user_count() == 1

        # Invalid additions
        assert manager.add_user("", "Bob") is False
        assert manager.add_user("2", "") is False

    def test_get_user(self):
        """get_user returns user dict with id and name; returns None if not found."""
        manager = UserManager()
        manager.add_user("1", "Alice")

        user = manager.get_user("1")
        assert user == {"id": "1", "name": "Alice"}

        # Defensive copy check
        user["name"] = "Modified"
        assert manager.get_user("1")["name"] == "Alice"

        assert manager.get_user("999") is None

    def test_get_user_by_name(self):
        """get_user_by_name supports exact index hit and case-insensitive fallback."""
        manager = UserManager()
        manager.add_user("1", "Alice")
        manager.add_user("2", "Bob Smith")

        # Exact match
        assert manager.get_user_by_name("Alice") == {"id": "1", "name": "Alice"}
        assert manager.get_user_by_name("Bob Smith") == {"id": "2", "name": "Bob Smith"}

        # Case-insensitive match
        assert manager.get_user_by_name("alice") == {"id": "1", "name": "Alice"}
        assert manager.get_user_by_name("ALICE") == {"id": "1", "name": "Alice"}
        assert manager.get_user_by_name("bob smith") == {"id": "2", "name": "Bob Smith"}

        # Non-existent name
        assert manager.get_user_by_name("Charlie") is None
        assert manager.get_user_by_name("") is None

    def test_search_users(self):
        """search_users performs case-insensitive substring matching."""
        manager = UserManager()
        manager.add_user("1", "Alice Wonderland")
        manager.add_user("2", "Bob Marley")
        manager.add_user("3", "Charlie Chaplin")

        # Substring search: "li" is in "Alice" and "Charlie"
        results = manager.search_users("li")
        assert len(results) == 2
        names = {u["name"] for u in results}
        assert names == {"Alice Wonderland", "Charlie Chaplin"}

        # Case-insensitive search
        results = manager.search_users("MARLEY")
        assert len(results) == 1
        assert results[0]["id"] == "2"

        # Empty query matches all users
        assert len(manager.search_users("")) == 3

        # Non-matching query returns empty list
        assert manager.search_users("xyz123") == []

    def test_remove_user(self):
        """remove_user deletes user record and cleans up name index."""
        manager = UserManager()
        manager.add_user("1", "Alice")
        assert manager.get_user_count() == 1

        assert manager.remove_user("1") is True
        assert manager.get_user_count() == 0
        assert manager.exists("1") is False
        assert manager.get_user("1") is None
        assert manager.get_user_by_name("Alice") is None

        # Removing absent user returns False
        assert manager.remove_user("1") is False
        assert manager.remove_user("999") is False

    def test_get_all_users(self):
        """get_all_users returns copies of all registered users."""
        manager = UserManager()
        manager.add_user("1", "Alice")
        manager.add_user("2", "Bob")

        all_users = manager.get_all_users()
        assert len(all_users) == 2
        user_ids = {u["id"] for u in all_users}
        assert user_ids == {"1", "2"}

    def test_clear_manager(self):
        """clear() resets user registry and name index."""
        manager = UserManager()
        manager.add_user("1", "Alice")
        manager.add_user("2", "Bob")

        manager.clear()
        assert manager.get_user_count() == 0
        assert manager.get_all_users() == []
        assert manager.get_user("1") is None
        assert manager.get_user_by_name("Alice") is None

    def test_repr(self):
        """repr should display user count."""
        manager = UserManager()
        manager.add_user("1", "Alice")
        assert "users=1" in repr(manager)

    def test_user_manager_type_safety_and_whitespace(self):
        """Type safety and whitespace input handling in UserManager."""
        manager = UserManager()
        # Invalid types
        assert manager.add_user(123, "Alice") is False  # type: ignore
        assert manager.add_user("1", 456) is False  # type: ignore
        assert manager.add_user(None, "Alice") is False  # type: ignore
        assert manager.add_user("1", None) is False  # type: ignore
        # Whitespace-only strings
        assert manager.add_user("   ", "Alice") is False
        assert manager.add_user("1", "   ") is False
        assert manager.add_user("  \t\n  ", "  ") is False
        assert manager.get_user_count() == 0

        # Stripping behavior
        assert manager.add_user(" 1 ", " Alice ") is True
        assert manager.exists("1") is True
        assert manager.exists(" 1 ") is True
        assert manager.get_user("1")["name"] == "Alice"
        assert manager.get_user_by_name(" Alice ")["id"] == "1"

        # Lookup with invalid types
        assert manager.get_user(123) is None  # type: ignore
        assert manager.get_user_by_name(None) is None  # type: ignore
        assert manager.search_users(123) == []  # type: ignore
        assert manager.exists(None) is False  # type: ignore



class TestDataHandler:
    """Unit tests for the DataHandler persistence class."""

    def test_load_network_success(self):
        """Verify loading the actual dataset."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(base_dir, "data", "sample_small.json")
        if not os.path.exists(filepath):
            filepath = os.path.join(base_dir, "data", "users.json")
        user_manager, social_graph = DataHandler.load_network(filepath)

        # 12 users
        assert user_manager.get_user_count() == 12
        assert social_graph.get_user_count() == 12

        # 15 friendships
        assert social_graph.get_friendship_count() == 15

        # Check specific user records
        alice = user_manager.get_user("1")
        assert alice is not None
        assert alice["name"] == "Alice"

        liam = user_manager.get_user("12")
        assert liam is not None
        assert liam["name"] == "Liam"

        # Check connections
        assert social_graph.are_friends("1", "2") is True
        assert social_graph.are_friends("1", "3") is True
        assert social_graph.are_friends("1", "4") is True
        assert social_graph.get_friends("1") == {"2", "3", "4"}

        # Liam is isolated
        assert social_graph.get_friends("12") == set()

    def test_load_network_missing_file(self):
        """Loading a non-existent file gracefully returns empty instances."""
        missing_path = "/non/existent/path/network_missing.json"
        user_manager, social_graph = DataHandler.load_network(missing_path)

        assert isinstance(user_manager, UserManager)
        assert isinstance(social_graph, SocialGraph)
        assert user_manager.get_user_count() == 0
        assert social_graph.get_user_count() == 0
        assert social_graph.get_friendship_count() == 0

    def test_load_network_corrupted_json(self, tmp_path):
        """Loading malformed JSON gracefully returns empty instances."""
        corrupt_file = tmp_path / "corrupt.json"
        corrupt_file.write_text("{ this is: not valid json !!!", encoding="utf-8")

        user_manager, social_graph = DataHandler.load_network(str(corrupt_file))
        assert isinstance(user_manager, UserManager)
        assert isinstance(social_graph, SocialGraph)
        assert user_manager.get_user_count() == 0
        assert social_graph.get_user_count() == 0

    def test_load_network_missing_users_key(self, tmp_path):
        """Loading JSON with only friendships auto-populates users in both manager and graph."""
        data_file = tmp_path / "only_friendships.json"
        data = {
            "friendships": [["A", "B"], ["B", "C"]]
        }
        data_file.write_text(json.dumps(data), encoding="utf-8")

        user_manager, social_graph = DataHandler.load_network(str(data_file))
        assert social_graph.get_user_count() == 3
        assert social_graph.get_friendship_count() == 2
        assert user_manager.get_user_count() == 3
        assert user_manager.exists("A")
        assert user_manager.exists("B")
        assert user_manager.exists("C")

    def test_save_and_load_roundtrip(self, tmp_path):
        """Verify save_network writes valid JSON and round-trips correctly."""
        save_file = tmp_path / "saved_network.json"

        # Create custom network
        um = UserManager()
        sg = SocialGraph()

        um.add_user("101", "Zara")
        um.add_user("102", "Yusuf")
        um.add_user("103", "Xavier")
        um.add_user("104", "Wendy")  # Isolated

        sg.add_user("101")
        sg.add_user("102")
        sg.add_user("103")
        sg.add_user("104")

        sg.add_friendship("101", "102")
        sg.add_friendship("102", "103")

        # Save network
        save_result = DataHandler.save_network(um, sg, str(save_file))
        assert save_result is True
        assert save_file.exists()

        # Validate saved JSON structure
        with open(save_file, "r", encoding="utf-8") as f:
            saved_data = json.load(f)

        assert "users" in saved_data
        assert "friendships" in saved_data
        assert len(saved_data["users"]) == 4
        assert len(saved_data["friendships"]) == 2

        # Reload using DataHandler
        loaded_um, loaded_sg = DataHandler.load_network(str(save_file))

        assert loaded_um.get_user_count() == 4
        assert loaded_sg.get_user_count() == 4
        assert loaded_sg.get_friendship_count() == 2

        assert loaded_um.get_user("101")["name"] == "Zara"
        assert loaded_um.get_user("104")["name"] == "Wendy"
        assert loaded_sg.are_friends("101", "102") is True
        assert loaded_sg.are_friends("102", "103") is True
        assert loaded_sg.are_friends("101", "103") is False
        assert loaded_sg.get_friends("104") == set()

    def test_save_network_with_unregistered_graph_user(self, tmp_path):
        """Graph contains a user not explicitly in UserManager; save should still include them."""
        save_file = tmp_path / "extra_users.json"
        um = UserManager()
        sg = SocialGraph()

        um.add_user("1", "Alice")
        sg.add_user("1")
        # Add user "2" and friendship directly to graph without adding to um
        sg.add_friendship("1", "2")

        assert DataHandler.save_network(um, sg, str(save_file)) is True

        loaded_um, loaded_sg = DataHandler.load_network(str(save_file))
        assert loaded_um.exists("1")
        assert loaded_um.exists("2")
        assert loaded_sg.are_friends("1", "2")

    def test_path_traversal_prevention_on_system_paths(self):
        """Path traversal or targeting restricted system paths should be blocked."""
        um = UserManager()
        sg = SocialGraph()
        assert DataHandler.is_safe_filepath("/etc/passwd") is False
        assert DataHandler.is_safe_filepath("/etc/shadow") is False
        assert DataHandler.is_safe_filepath("/root/.ssh/id_rsa") is False
        assert DataHandler.is_safe_filepath("safe_file.json\0malicious.json") is False
        assert DataHandler.is_safe_filepath(None) is False  # type: ignore

        # Attempting to save to /etc/evil.json should return False
        assert DataHandler.save_network(um, sg, "/etc/evil_social_network.json") is False

        # Attempting to load from /etc/passwd should return safe empty instances
        lum, lsg = DataHandler.load_network("/etc/passwd")
        assert lum.get_user_count() == 0
        assert lsg.get_user_count() == 0

    def test_path_traversal_with_allowed_base_dir(self, tmp_path):
        """Constraining file operations to allowed_base_dir."""
        allowed_dir = tmp_path / "sandbox"
        allowed_dir.mkdir()
        safe_file = allowed_dir / "network.json"
        outside_file = tmp_path / "outside.json"

        assert DataHandler.is_safe_filepath(str(safe_file), allowed_base_dir=str(allowed_dir)) is True
        assert DataHandler.is_safe_filepath(str(outside_file), allowed_base_dir=str(allowed_dir)) is False

        um = UserManager()
        sg = SocialGraph()
        # Save outside allowed dir fails
        assert DataHandler.save_network(um, sg, str(outside_file), allowed_base_dir=str(allowed_dir)) is False
        # Save inside allowed dir succeeds
        assert DataHandler.save_network(um, sg, str(safe_file), allowed_base_dir=str(allowed_dir)) is True

