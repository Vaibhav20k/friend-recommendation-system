"""Unit test suite for the custom HashTable implementation (Separate Chaining)."""

import pytest
from core.hash_table import HashTable


class TestHashTable:
    """Tests covering separate chaining, polynomial hashing, rehashing, and metrics."""

    def test_init(self):
        """Test default and custom initialization."""
        ht = HashTable()
        assert len(ht) == 0
        assert ht.stats()["capacity"] == 16
        assert ht.stats()["load_factor"] == 0.0

        ht_custom = HashTable(initial_capacity=8, max_load_factor=0.5)
        assert ht_custom.stats()["capacity"] == 8

        ht_invalid = HashTable(initial_capacity=0)
        assert ht_invalid.stats()["capacity"] == 16

    def test_put_and_get(self):
        """Test standard put, get, and bracket access."""
        ht = HashTable()
        ht.put("alice", "1")
        ht.put("bob", "2")
        ht["charlie"] = "3"

        assert len(ht) == 3
        assert ht.get("alice") == "1"
        assert ht.get("bob") == "2"
        assert ht["charlie"] == "3"
        assert ht.get("nonexistent") is None
        assert ht.get("nonexistent", "default_val") == "default_val"

        with pytest.raises(KeyError):
            _ = ht["missing_key"]

    def test_overwrite_existing_key(self):
        """Overwriting an existing key should update value without increasing size."""
        ht = HashTable()
        ht.put("user1", "original")
        assert len(ht) == 1
        assert ht.get("user1") == "original"

        ht.put("user1", "updated")
        assert len(ht) == 1
        assert ht.get("user1") == "updated"

        ht["user1"] = "bracket_updated"
        assert len(ht) == 1
        assert ht["user1"] == "bracket_updated"

    def test_remove(self):
        """Test removal via remove() and del syntax."""
        ht = HashTable()
        ht.put("k1", "v1")
        ht.put("k2", "v2")
        ht.put("k3", "v3")

        assert ht.remove("k2") is True
        assert len(ht) == 2
        assert "k2" not in ht
        assert ht.get("k2") is None
        assert ht.remove("k2") is False

        del ht["k1"]
        assert len(ht) == 1
        assert "k1" not in ht

        with pytest.raises(KeyError):
            del ht["missing_key"]

    def test_contains(self):
        """Test 'in' operator support."""
        ht = HashTable()
        ht.put("alpha", 100)
        assert "alpha" in ht
        assert "beta" not in ht

    def test_collision_handling(self):
        """Test that separate chaining correctly stores multiple items in same bucket."""
        # Force table size 2 to guarantee collisions
        ht = HashTable(initial_capacity=2, max_load_factor=10.0)
        keys = ["apple", "banana", "cherry", "date", "elderberry"]
        for i, k in enumerate(keys):
            ht.put(k, i)

        assert len(ht) == 5
        for i, k in enumerate(keys):
            assert ht.get(k) == i

        stats = ht.stats()
        assert stats["longest_chain"] > 1
        assert stats["collisions"] > 0

    def test_automatic_resizing_and_rehashing(self):
        """Test that table doubles capacity when load factor exceeds threshold and retains all elements."""
        ht = HashTable(initial_capacity=4, max_load_factor=0.75)
        # Capacity is 4, max load before resize is 4 * 0.75 = 3
        ht.put("k1", 1)
        ht.put("k2", 2)
        ht.put("k3", 3)
        assert ht.stats()["capacity"] == 4

        # 4th insert exceeds 0.75 load factor -> capacity doubles to 8
        ht.put("k4", 4)
        assert ht.stats()["capacity"] == 8
        assert ht.stats()["load_factor"] <= 0.75

        # Insert up to 30 items
        for i in range(5, 31):
            ht.put(f"user_{i}", i)
            assert ht.stats()["load_factor"] <= 0.75

        assert len(ht) == 30
        for i in range(1, 5):
            assert ht.get(f"k{i}") == i
        for i in range(5, 31):
            assert ht.get(f"user_{i}") == i

    def test_keys_values_items_and_iteration(self):
        """Test iteration and list generators."""
        ht = HashTable()
        data = {"u1": 10, "u2": 20, "u3": 30}
        for k, v in data.items():
            ht.put(k, v)

        assert sorted(ht.keys()) == ["u1", "u2", "u3"]
        assert sorted(ht.values()) == [10, 20, 30]
        assert sorted(ht.items()) == [("u1", 10), ("u2", 20), ("u3", 30)]
        assert sorted(list(ht)) == ["u1", "u2", "u3"]

    def test_clear(self):
        """Test clearing hash table."""
        ht = HashTable()
        ht.put("a", 1)
        ht.put("b", 2)
        ht.clear()
        assert len(ht) == 0
        assert ht.stats()["size"] == 0
        assert "a" not in ht

    def test_stats_and_buckets(self):
        """Test inspection helpers for UI visualization."""
        ht = HashTable(initial_capacity=8)
        ht.put("a", 1)
        ht.put("b", 2)
        stats = ht.stats()
        assert stats["size"] == 2
        assert stats["capacity"] == 8
        assert stats["load_factor"] == 0.25
        assert isinstance(stats["chain_lengths"], list)
        assert len(stats["chain_lengths"]) == 8

        buckets = ht.buckets()
        assert len(buckets) == 8
        b_idx = ht.bucket_of("a")
        assert 0 <= b_idx < 8
        assert ("a", 1) in buckets[b_idx]
