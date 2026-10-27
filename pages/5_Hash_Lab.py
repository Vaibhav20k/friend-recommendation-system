"""Custom Hash Table Laboratory & Benchmark Page."""

import time
import random
import string
import streamlit as st
import pandas as pd

from ui.state import get_user_manager, init_session_state
from ui.styles import apply_custom_styles
from core.hash_table import HashTable

init_session_state()
apply_custom_styles()

um = get_user_manager()
ht = um.username_index

st.title("🧪 Hash Table Lab")
st.caption("Internal Inspection of the Hand-Written Separate-Chaining Hash Table and Academic Benchmarking")

# Theory Callout
with st.expander("ℹ️ How This Custom Hash Table Works (Academic Primer)", expanded=False):
    st.markdown(
        r"""
        This hash table is **hand-written from first principles in pure Python** (no Python `dict` used for internal bucket storage):
        1. **Polynomial Rolling Hash Function**:
           $$H(s) = \left( \sum_{i=0}^{k-1} \text{ord}(s[i]) \times 31^i \right)$$
           The prime multiplier $p = 31$ provides excellent entropy across ASCII character sequences.
        2. **Compression Map**:
           $$\text{bucket\_index} = H(s) \pmod m$$
           Where $m$ is the table capacity (number of buckets).
        3. **Collision Resolution via Separate Chaining**:
           Each bucket contains a dynamic list of `(key, value)` pairs. When collisions occur, items chain in that bucket.
        4. **Automatic Rehashing ($O(1)$ Amortized Guarantee)**:
           When the **Load Factor** $\alpha = \frac{n}{m} > 0.75$, the capacity doubles ($m' = 2m$) and all keys are rehashed.
        """
    )

# Section 1: Live Key Query & Bucket Explorer
st.subheader("🔍 Live Username Hash & Bucket Inspector")
search_query = st.text_input(
    "Enter a username handle to hash and inspect (e.g. 'zara_patel', 'aarav_sharma', or custom key):",
    value="zara_patel",
).strip().lower()

if search_query:
    raw_hash = ht._hash(search_query)
    bucket_idx = ht.bucket_of(search_query)
    all_buckets = ht.buckets()
    chain = all_buckets[bucket_idx] if bucket_idx < len(all_buckets) else []

    found_val = ht.get(search_query)

    col_h1, col_h2, col_h3 = st.columns(3)
    col_h1.metric("Polynomial Hash Code", f"{raw_hash:,}")
    col_h2.metric("Target Bucket Index", f"[{bucket_idx}] of {ht.stats()['capacity']}")
    col_h3.metric("Chain Length in Bucket", len(chain))

    with st.container(border=True):
        if found_val is not None:
            user_rec = um.get_user(found_val)
            user_display = user_rec["name"] if user_rec else f"User {found_val}"
            st.success(f"✅ **Key Found!** Username `@{search_query}` maps to Student ID: `{found_val}` (**{user_display}**)")
        else:
            st.warning(f"❌ **Key Not Found!** Username `@{search_query}` is not currently stored in the table.")

        st.markdown(f"**Contents of Bucket `[{bucket_idx}]`:**")
        if chain:
            chain_str = " ➔ ".join(f"`({k}: {v})`" for k, v in chain)
            st.code(f"Head ➔ {chain_str} ➔ None")
        else:
            st.caption("This bucket is currently empty.")

st.markdown("---")

# Section 2: Real-Time Structural Statistics
st.subheader("📈 Real-Time Hash Table Metrics")
stats = ht.stats()

m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("Items (n)", stats["size"])
m2.metric("Capacity (m)", stats["capacity"])
m3.metric("Load Factor (α)", f"{stats['load_factor']:.3f}", help="Threshold = 0.75")
m4.metric("Longest Chain", stats["longest_chain"])
m5.metric("Collisions", stats["collisions"])
m6.metric("Empty Buckets", stats["empty_buckets"])

# Bucket Visualizer Bar Chart
st.subheader("📊 Bucket Chain Length Distribution")
chain_data = pd.DataFrame({
    "Bucket Index": [f"[{i}]" for i in range(stats["capacity"])],
    "Chain Length": stats["chain_lengths"],
})
st.bar_chart(chain_data.set_index("Bucket Index"), height=220)

st.markdown("---")

# Section 3: Empirical Benchmark (Hash Table O(1) vs Linear Scan O(N))
st.subheader("⚡ Benchmark: Custom Hash Table $O(1)$ vs Linear List Scan $O(N)$")
st.caption("Demonstrates the dramatic theoretical and empirical speedup of hash table indexing over list scans.")

bench_size = st.radio("Benchmark Dataset Size:", options=[1000, 10000], horizontal=True)

if st.button("🚀 Run Empirical Benchmark", type="primary"):
    with st.spinner(f"Generating {bench_size:,} synthetic usernames and executing timing benchmark..."):
        # Generate random unique strings
        random.seed(42)
        bench_keys = []
        for i in range(bench_size):
            prefix = "".join(random.choices(string.ascii_lowercase, k=8))
            bench_keys.append(f"{prefix}_{i}")

        # Populate custom HashTable
        test_ht = HashTable(initial_capacity=16)
        for k in bench_keys:
            test_ht.put(k, f"val_{k}")

        # Populate Python List of (key, value) pairs for linear scan
        test_list = [(k, f"val_{k}") for k in bench_keys]

        # Select 200 probe keys (100 present, 100 absent)
        probes = random.sample(bench_keys, min(100, len(bench_keys)))
        absent_probes = [f"absent_{i}" for i in range(100)]
        all_probes = probes + absent_probes

        # Timing 1: Custom Hash Table lookups
        t0 = time.perf_counter()
        for p in all_probes:
            _ = test_ht.get(p)
        t_hash = (time.perf_counter() - t0) * 1000.0  # milliseconds

        # Timing 2: Linear List Scan
        def linear_scan(lst, key):
            for k, v in lst:
                if k == key:
                    return v
            return None

        t0 = time.perf_counter()
        for p in all_probes:
            _ = linear_scan(test_list, p)
        t_linear = (time.perf_counter() - t0) * 1000.0  # milliseconds

        speedup = (t_linear / t_hash) if t_hash > 0 else 1.0

        b_col1, b_col2, b_col3 = st.columns(3)
        b_col1.metric("Hash Table O(1) Total Time", f"{t_hash:.3f} ms")
        b_col2.metric("Linear Scan O(N) Total Time", f"{t_linear:.3f} ms")
        b_col3.metric("Empirical Speedup Factor", f"{speedup:.1f}x Faster")

        # Bar chart comparison
        bench_df = pd.DataFrame({
            "Method": ["Custom HashTable (O(1))", "Linear List Scan (O(N))"],
            "Time (ms)": [t_hash, t_linear],
        })
        st.bar_chart(bench_df.set_index("Method"), height=240)

        st.success(
            f"🎯 **Empirical Proof:** The custom Hash Table achieved an amortized **{speedup:.1f}x speedup** "
            f"across {len(all_probes)} queries on {bench_size:,} elements!"
        )
