"""Integration test suite for the Smart Friend Recommendation System.

Validates end-to-end multi-module workflows:
- Workflow 1: Complete lifecycle of loading network -> querying recommendations -> adding friend
  -> candidate removed from recommendations -> friends of new friend become new candidates -> persistence roundtrip.
- Workflow 2: Dynamic shortest-path recalculation under network edge addition
  (Alice to Kelly connection drops from distance 4 to distance 2 via shortcut edge).
- Workflow 3: Cascading user removal across graph topology, mutual friend ranking, BFS paths, and JSON persistence.
- Workflow 4: New user onboarding session (register user, form friendships, compute recommendations, BFS routing).
"""

import os
import pytest
from core.graph import SocialGraph
from core.user_manager import UserManager
from core.bfs import find_shortest_connection
from core.recommendation import get_friend_recommendations
from utils.data_handler import DataHandler

DATA_FILE = "/home/vaibhav/friend-recommendation-system/data/users.json"


@pytest.fixture
def loaded_system():
    """Fixture providing freshly loaded UserManager and SocialGraph from canonical dataset."""
    assert os.path.exists(DATA_FILE), f"Dataset file not found at {DATA_FILE}"
    um, sg = DataHandler.load_network(DATA_FILE)
    return um, sg


class TestSystemIntegrationWorkflows:
    """Integration test suite testing interactions between Graph, UserManager, BFS, Recommendation, and DataHandler."""

    def test_workflow_1_friend_addition_recommendation_evolution_and_persistence(
        self, loaded_system, tmp_path
    ):
        """Workflow 1:
        1. Load dataset.
        2. Query recommendations for Alice ("1") -> Emma ("5") is top candidate (mutuals: Bob, Charlie).
        3. Alice adds Emma as friend.
        4. Emma is removed from Alice's recommendations (direct friends excluded).
        5. Emma's friend Hannah ("8") becomes a new 2-hop recommendation candidate for Alice.
        6. Save network to JSON and reload to ensure complete persistence fidelity.
        """
        user_manager, social_graph = loaded_system

        # Step 1: Initial state validation
        assert user_manager.get_user_count() == 12
        assert social_graph.get_friendship_count() == 15
        assert social_graph.are_friends("1", "5") is False

        # Step 2: Query recommendations for Alice ("1")
        initial_recs = get_friend_recommendations(social_graph, "1")
        assert len(initial_recs) == 3
        # Top candidate is Emma ("5") with 2 mutual friends (Bob: 2, Charlie: 3)
        assert initial_recs[0]["user_id"] == "5"
        assert initial_recs[0]["mutual_count"] == 2
        assert set(initial_recs[0]["mutual_friends"]) == {"2", "3"}

        # Hannah ("8") is currently 3 hops away from Alice (Alice -> Bob -> Emma -> Hannah)
        # So Hannah is NOT in Alice's 2-hop recommendations
        initial_rec_ids = {r["user_id"] for r in initial_recs}
        assert "8" not in initial_rec_ids

        # Step 3: Alice accepts recommendation and adds Emma as friend
        assert social_graph.add_friendship("1", "5") is True
        assert social_graph.are_friends("1", "5") is True
        assert social_graph.get_friendship_count() == 16

        # Step 4: Re-query recommendations for Alice
        updated_recs = get_friend_recommendations(social_graph, "1")
        updated_rec_ids = {r["user_id"] for r in updated_recs}

        # Emma is now a direct friend, so Emma MUST be excluded
        assert "5" not in updated_rec_ids
        assert "2" not in updated_rec_ids  # Bob (direct)
        assert "3" not in updated_rec_ids  # Charlie (direct)
        assert "4" not in updated_rec_ids  # David (direct)

        # Step 5: Emma's friends (Hannah: "8") now become 2-hop candidates for Alice!
        assert "8" in updated_rec_ids
        hannah_rec = next(r for r in updated_recs if r["user_id"] == "8")
        # Alice and Hannah now share Emma ("5") as a mutual friend
        assert "5" in hannah_rec["mutual_friends"]

        # Step 6: Verify Persistence Round-Trip
        save_path = tmp_path / "workflow_1_persisted.json"
        save_ok = DataHandler.save_network(user_manager, social_graph, str(save_path))
        assert save_ok is True

        reloaded_um, reloaded_sg = DataHandler.load_network(str(save_path))
        assert reloaded_um.get_user_count() == 12
        assert reloaded_sg.get_friendship_count() == 16
        assert reloaded_sg.are_friends("1", "5") is True

        reloaded_recs = get_friend_recommendations(reloaded_sg, "1")
        reloaded_rec_ids = {r["user_id"] for r in reloaded_recs}
        assert "5" not in reloaded_rec_ids
        assert "8" in reloaded_rec_ids

    def test_workflow_2_bfs_path_recalculation_after_shortcut_edge(self, loaded_system):
        """Workflow 2:
        1. In standard network, shortest path from Alice ("1") to Kelly ("11") has distance 4.
        2. Add a shortcut edge connecting Alice ("1") to Jack ("10").
        3. Recalculate BFS path: distance drops from 4 hops to 2 hops (Alice -> Jack -> Kelly).
        4. Verify path validity, edge existence, and symmetry.
        """
        _, social_graph = loaded_system

        # Step 1: Initial path from Alice ("1") to Kelly ("11")
        initial_path, initial_dist = find_shortest_connection(social_graph, "1", "11")
        assert initial_dist == 4
        assert len(initial_path) == 5
        assert initial_path[0] == "1"
        assert initial_path[-1] == "11"

        # Verify initial path edges all exist
        for i in range(len(initial_path) - 1):
            assert social_graph.are_friends(initial_path[i], initial_path[i + 1])

        # Jack ("10") is directly connected to Kelly ("11")
        assert social_graph.are_friends("10", "11") is True

        # Step 2: Add shortcut edge between Alice ("1") and Jack ("10")
        assert social_graph.add_friendship("1", "10") is True
        assert social_graph.are_friends("1", "10") is True

        # Step 3: Recalculate shortest path from Alice ("1") to Kelly ("11")
        new_path, new_dist = find_shortest_connection(social_graph, "1", "11")

        # Distance dramatically drops from 4 to 2!
        assert new_dist == 2
        assert new_path == ["1", "10", "11"]

        # Step 4: Verify reverse symmetry
        rev_path, rev_dist = find_shortest_connection(social_graph, "11", "1")
        assert rev_dist == 2
        assert rev_path == ["11", "10", "1"]

    def test_workflow_3_cascading_user_removal(self, loaded_system, tmp_path):
        """Workflow 3:
        1. Remove Frank ("6") from the network.
        2. Verify user removal cascades through:
           - SocialGraph: Frank's node and all incident edges removed.
           - UserManager: Frank's identity and name lookup cleaned up.
           - Recommendations: Frank is removed as candidate and as mutual friend.
           - BFS: Shortest paths through Frank are severed and rerouted.
           - Persistence: Saved JSON excludes Frank and Frank's edges.
        """
        user_manager, social_graph = loaded_system

        # Pre-condition checks for Frank ("6")
        assert user_manager.exists("6") is True
        assert user_manager.get_user("6")["name"] == "Frank"
        assert social_graph.has_user("6") is True
        frank_friends = social_graph.get_friends("6")
        assert frank_friends == {"2", "4", "10"}  # Bob, David, Jack

        # Frank is a recommendation candidate for Alice ("1") before removal
        initial_alice_recs = get_friend_recommendations(social_graph, "1")
        assert any(r["user_id"] == "6" for r in initial_alice_recs)

        # Alice ("1") to Jack ("10") path goes through Frank ("6"): ["1", "2", "6", "10"] (distance 3)
        path_before, dist_before = find_shortest_connection(social_graph, "1", "10")
        assert dist_before == 3
        assert "6" in path_before

        # Step 1: Remove Frank ("6")
        assert user_manager.remove_user("6") is True
        assert social_graph.remove_user("6") is True

        # Step 2: Verify Graph Topology Cascading
        assert social_graph.has_user("6") is False
        assert user_manager.exists("6") is False
        assert user_manager.get_user("6") is None
        assert user_manager.get_user_by_name("Frank") is None

        # Verify Frank is eliminated from Bob ("2"), David ("4"), and Jack ("10")
        assert "6" not in social_graph.get_friends("2")
        assert "6" not in social_graph.get_friends("4")
        assert "6" not in social_graph.get_friends("10")
        # 15 edges - 3 edges incident on Frank = 12 edges remain
        assert social_graph.get_friendship_count() == 12

        # Step 3: Verify Recommendation Engine Cascading
        updated_alice_recs = get_friend_recommendations(social_graph, "1")
        # Frank is completely gone from recommendation candidates
        assert not any(r["user_id"] == "6" for r in updated_alice_recs)
        # Frank is nowhere mentioned in any mutual friend lists
        for rec in updated_alice_recs:
            assert "6" not in rec["mutual_friends"]

        # Step 4: Verify BFS Path Rerouting
        # Path from Alice ("1") to Frank ("6") is now nonexistent
        path_to_frank, dist_to_frank = find_shortest_connection(social_graph, "1", "6")
        assert path_to_frank is None
        assert dist_to_frank == -1

        # Path from Alice ("1") to Jack ("10") cannot use Frank anymore.
        # It must reroute around via Charlie ("3") -> Grace ("7") -> Ian ("9") -> Kelly ("11") -> Jack ("10")
        path_after, dist_after = find_shortest_connection(social_graph, "1", "10")
        assert dist_after == 5
        assert "6" not in path_after
        assert path_after == ["1", "3", "7", "9", "11", "10"]

        # Step 5: Verify Persistence Exclusion
        save_path = tmp_path / "workflow_3_frank_removed.json"
        assert DataHandler.save_network(user_manager, social_graph, str(save_path)) is True

        reloaded_um, reloaded_sg = DataHandler.load_network(str(save_path))
        assert reloaded_um.get_user_count() == 11
        assert reloaded_sg.get_user_count() == 11
        assert reloaded_sg.get_friendship_count() == 12
        assert not reloaded_um.exists("6")
        assert not reloaded_sg.has_user("6")

    def test_workflow_4_new_user_onboarding_and_graph_integration(self, loaded_system):
        """Workflow 4:
        1. Onboard a new user 'Maya' with ID '13'.
        2. Connect Maya to Bob ('2') and Charlie ('3').
        3. Query recommendations for Maya -> Alice ('1') and Emma ('5') should be recommended.
        4. Calculate shortest path from Maya to Kelly ('11').
        """
        user_manager, social_graph = loaded_system

        # Onboard Maya
        assert user_manager.add_user("13", "Maya Lin") is True
        assert social_graph.add_user("13") is True

        # Connect Maya to Bob and Charlie
        social_graph.add_friendship("13", "2")
        social_graph.add_friendship("13", "3")

        # Query recommendations for Maya
        maya_recs = get_friend_recommendations(social_graph, "13")
        maya_rec_ids = {r["user_id"] for r in maya_recs}

        # Alice ("1") shares Bob ("2") and Charlie ("3") with Maya (2 mutuals)
        # Emma ("5") shares Bob ("2") and Charlie ("3") with Maya (2 mutuals)
        assert "1" in maya_rec_ids
        assert "5" in maya_rec_ids

        alice_rec = next(r for r in maya_recs if r["user_id"] == "1")
        assert alice_rec["mutual_count"] == 2
        assert set(alice_rec["mutual_friends"]) == {"2", "3"}

        # BFS path from Maya ("13") to Kelly ("11")
        path, dist = find_shortest_connection(social_graph, "13", "11")
        # Maya -> Bob (2) -> Frank (6) -> Jack (10) -> Kelly (11) = 4 hops
        # Or Maya -> Charlie (3) -> Grace (7) -> Ian (9) -> Kelly (11) = 4 hops
        assert dist == 4
        assert path[0] == "13"
        assert path[-1] == "11"
