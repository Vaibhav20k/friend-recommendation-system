"""Custom Hash Table module with separate chaining collision resolution.

Responsible for:
- Pure Python hand-written hash table data structure (no Python dict for storage).
- Separate chaining (linked list / array buckets) collision resolution.
- Polynomial rolling hash function on string keys.
- Automatic dynamic resizing and rehashing when load factor exceeds 0.75.
- Exposing bucket distributions, chain lengths, and collision metrics for academic demonstration.

Academic & Viva Context:
- Hash Function: Polynomial rolling hash:
    hash(s) = sum(ord(s[i]) * p^i) mod capacity
    where p = 31 is an odd prime giving good distribution over character sequences.
- Collision Resolution: Separate Chaining (each bucket contains a list of (key, value) pairs).
- Load Factor alpha = n / m (where n = item count, m = capacity).
- Rehashing: When alpha > 0.75, capacity is doubled (m' = 2 * m) and all items
  are re-hashed into new buckets in O(n) time, guaranteeing O(1) amortized lookup.
"""

from typing import Any, Dict, Iterator, List, Optional, Tuple


class HashTable:
    """A hand-written hash table implementing separate chaining for collision resolution.

    Attributes:
        _capacity: The number of buckets (table size m).
        _size: The number of key-value pairs stored (n).
        _buckets: A list of buckets, where each bucket is a list of (key, value) tuples.
        _max_load_factor: Load factor threshold triggering automatic rehashing (default: 0.75).
        _prime: Prime multiplier for polynomial rolling hash (default: 31).
    """

    def __init__(self, initial_capacity: int = 16, max_load_factor: float = 0.75) -> None:
        """Initialize an empty HashTable.

        Args:
            initial_capacity: Starting bucket array size (default: 16). Must be >= 1.
            max_load_factor: Load factor threshold before table doubles in size (default: 0.75).
        """
        if initial_capacity < 1:
            initial_capacity = 16
        self._capacity: int = int(initial_capacity)
        self._max_load_factor: float = float(max_load_factor)
        self._size: int = 0
        self._prime: int = 31
        self._buckets: List[List[Tuple[str, Any]]] = [[] for _ in range(self._capacity)]

    def _hash(self, key: str) -> int:
        """Compute the raw polynomial rolling hash for a string key.

        Formula:
            H(s) = sum_{i=0}^{k-1} (ord(s[i]) * 31^i)

        Time Complexity:
            O(L) where L is the length of key string.

        Args:
            key: String key to hash.

        Returns:
            Non-negative integer hash code.
        """
        h = 0
        p_pow = 1
        for ch in key:
            h = (h + ord(ch) * p_pow)
            p_pow = (p_pow * self._prime)
        return h

    def bucket_of(self, key: str) -> int:
        """Return the bucket index where the given key maps.

        Formula:
            index = H(key) % capacity

        Args:
            key: String key.

        Returns:
            Integer bucket index in [0, capacity - 1].
        """
        if not isinstance(key, str):
            key = str(key)
        return self._hash(key) % self._capacity

    def put(self, key: str, value: Any) -> None:
        """Insert or update a key-value pair.

        If key already exists, updates its value.
        If adding a new key causes load factor to exceed 0.75, triggers rehashing.

        Time Complexity:
            Average Case: O(1 + alpha) where alpha <= 0.75 is load factor.
            Worst Case: O(n) on hash collision clustering or when resizing.

        Args:
            key: String key.
            value: Associated value.
        """
        if not isinstance(key, str):
            key = str(key)

        idx = self.bucket_of(key)
        bucket = self._buckets[idx]

        # Check for existing key to overwrite
        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return

        # Check if resize is required before inserting new key
        if (self._size + 1) / self._capacity > self._max_load_factor:
            self._resize(self._capacity * 2)
            idx = self.bucket_of(key)
            bucket = self._buckets[idx]

        bucket.append((key, value))
        self._size += 1

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """Retrieve the value associated with key, or default if not found.

        Time Complexity:
            Average Case: O(1).
            Worst Case: O(n).

        Args:
            key: String key.
            default: Value returned if key is missing.

        Returns:
            Stored value if found, else default.
        """
        if not isinstance(key, str):
            key = str(key)

        idx = self.bucket_of(key)
        for k, v in self._buckets[idx]:
            if k == key:
                return v
        return default

    def remove(self, key: str) -> bool:
        """Remove a key and its value from the hash table.

        Time Complexity:
            Average Case: O(1).
            Worst Case: O(n).

        Args:
            key: String key to remove.

        Returns:
            True if key was found and removed, False otherwise.
        """
        if not isinstance(key, str):
            key = str(key)

        idx = self.bucket_of(key)
        bucket = self._buckets[idx]
        for i, (k, _) in enumerate(bucket):
            if k == key:
                del bucket[i]
                self._size -= 1
                return True
        return False

    def _resize(self, new_capacity: int) -> None:
        """Rehash all key-value pairs into a new bucket array of size new_capacity.

        Time Complexity:
            O(n + m) where n is size and m is new_capacity.
        """
        old_buckets = self._buckets
        self._capacity = max(1, new_capacity)
        self._buckets = [[] for _ in range(self._capacity)]
        self._size = 0

        for bucket in old_buckets:
            for k, v in bucket:
                self.put(k, v)

    def stats(self) -> Dict[str, Any]:
        """Compute structural metrics and collision statistics for visualization and viva examination.

        Returns:
            Dictionary containing:
                - size: Total elements stored (n)
                - capacity: Number of buckets (m)
                - load_factor: Ratio n / m
                - longest_chain: Maximum number of elements in any single bucket
                - collisions: Total count of items that collide with an existing item in a bucket
                - empty_buckets: Number of buckets with 0 elements
                - chain_lengths: List of lengths for each bucket
        """
        chain_lengths = [len(b) for b in self._buckets]
        longest_chain = max(chain_lengths) if chain_lengths else 0
        empty_buckets = sum(1 for length in chain_lengths if length == 0)
        # Collisions: for any bucket with k > 1 elements, k - 1 elements collided
        collisions = sum(max(0, length - 1) for length in chain_lengths)
        load_factor = self._size / self._capacity if self._capacity > 0 else 0.0

        return {
            "size": self._size,
            "capacity": self._capacity,
            "load_factor": round(load_factor, 4),
            "longest_chain": longest_chain,
            "collisions": collisions,
            "empty_buckets": empty_buckets,
            "chain_lengths": chain_lengths,
        }

    def buckets(self) -> List[List[Tuple[str, Any]]]:
        """Return a defensive shallow copy of all buckets and their chains."""
        return [list(b) for b in self._buckets]

    def keys(self) -> List[str]:
        """Return list of all stored keys."""
        res: List[str] = []
        for b in self._buckets:
            for k, _ in b:
                res.append(k)
        return res

    def values(self) -> List[Any]:
        """Return list of all stored values."""
        res: List[Any] = []
        for b in self._buckets:
            for _, v in b:
                res.append(v)
        return res

    def items(self) -> List[Tuple[str, Any]]:
        """Return list of all (key, value) pairs."""
        res: List[Tuple[str, Any]] = []
        for b in self._buckets:
            for item in b:
                res.append(item)
        return res

    def clear(self) -> None:
        """Clear all entries and reset to default capacity."""
        self._capacity = 16
        self._size = 0
        self._buckets = [[] for _ in range(self._capacity)]

    def __contains__(self, key: str) -> bool:
        """Enable pythonic 'key in hash_table' syntax."""
        return self.get(key, None) is not None or any(
            k == key for k, _ in self._buckets[self.bucket_of(str(key))]
        )

    def __len__(self) -> int:
        """Enable len(hash_table)."""
        return self._size

    def __getitem__(self, key: str) -> Any:
        """Enable hash_table[key] syntax. Raises KeyError if key missing."""
        if not isinstance(key, str):
            key = str(key)
        idx = self.bucket_of(key)
        for k, v in self._buckets[idx]:
            if k == key:
                return v
        raise KeyError(f"Key not found in HashTable: '{key}'")

    def __setitem__(self, key: str, value: Any) -> None:
        """Enable hash_table[key] = value syntax."""
        self.put(key, value)

    def __delitem__(self, key: str) -> None:
        """Enable del hash_table[key] syntax. Raises KeyError if missing."""
        if not self.remove(key):
            raise KeyError(f"Key not found in HashTable: '{key}'")

    def __iter__(self) -> Iterator[str]:
        """Iterate over keys in the table."""
        for b in self._buckets:
            for k, _ in b:
                yield k

    def __repr__(self) -> str:
        """String representation showing size and capacity."""
        return f"HashTable(size={self._size}, capacity={self._capacity}, load_factor={self._size / self._capacity:.2f})"
