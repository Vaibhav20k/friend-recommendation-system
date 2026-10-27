"""Theory & Viva Voce Preparation Guide with Interactive Quiz."""

import streamlit as st
from ui.styles import apply_custom_styles

apply_custom_styles()

st.title("📖 Algorithm Theory & Master Viva Guide")
st.caption("Mathematical Models, Time & Space Complexities, Proofs, and Interactive Viva Examination Questions")

# Tabs for Organization
tab_theory, tab_quiz, tab_complexities = st.tabs(
    [
        "🧠 Core DSA Theory",
        "🎯 Interactive Viva Quiz",
        "⚡ Time & Space Complexity Matrix",
    ]
)

# -----------------------------------------------------------------------------
# TAB 1: Core Theory
# -----------------------------------------------------------------------------
with tab_theory:
    with st.expander("1. Graph Representation: Adjacency List (Pure Python)", expanded=True):
        st.markdown(
            r"""
            - **Mathematical Definition:** A social network is modeled as an unweighted, undirected graph 
              $G = (V, E)$, where $V$ represents registered student nodes and $E$ represents mutual friendships.
            - **Internal Structure:** A Python dictionary mapping each user ID to a `set` of neighbor user IDs (`Dict[str, Set[str]]`):
              ```python
              self._adj = {
                  "1": {"2", "3", "4"},
                  "2": {"1", "5"},
                  ...
              }
              ```
            - **Space Complexity:** $O(V + E)$ vs $O(V^2)$ for an Adjacency Matrix. Because social networks are sparse ($\text{avg degree} \ll |V|$), adjacency lists consume significantly less memory.
            - **Fast $O(1)$ Hash Operations:** Node existence (`u in graph`) and edge existence (`v in graph.get_friends(u)`) execute in $O(1)$ average time.
            - **Handshaking Lemma:** The sum of degrees across all vertices equals twice the total number of edges:
              $$\sum_{v \in V} \deg(v) = 2 \times |E|$$
            """
        )

    with st.expander("2. Breadth-First Search (BFS) & Shortest Path Optimality Proof", expanded=True):
        st.markdown(
            r"""
            - **Why BFS Guarantees Shortest Path in Unweighted Graphs:**
              1. **Layer-by-Layer FIFO Expansion:** Using `collections.deque`, BFS explores all vertices at distance $k$ before examining any vertex at distance $k+1$.
              2. **First-Encounter Optimality:** In an unweighted graph where every edge has unit cost $1$, when the target vertex is first dequeued from the FIFO queue, it must have been reached via the minimal possible number of edges.
              3. **Cycle Prevention:** A `visited` set prevents revisiting previously expanded nodes, preventing infinite loops in cyclic networks.
            - **Time Complexity:** $O(V + E)$ — each reachable vertex is enqueued and dequeued at most once, and each incident edge is traversed at most twice.
            - **Space Complexity:** $O(V)$ auxiliary memory for the queue, visited set, and predecessor pointer map.
            """
        )

    with st.expander("3. Custom Hash Table: Separate Chaining & Polynomial Rolling Hash", expanded=True):
        st.markdown(
            r"""
            - **Academic Motivation:** Built from first principles to demonstrate how Python's underlying `dict` works internally.
            - **Polynomial Rolling Hash:**
              $$H(s) = \left( \sum_{i=0}^{k-1} \text{ord}(s[i]) \times 31^i \right)$$
              Using prime multiplier $p = 31$ minimizes collisions for character strings.
            - **Bucket Mapping:** $\text{index} = H(s) \pmod m$ where $m$ is table capacity.
            - **Separate Chaining:** Colliding keys are stored in a linked list / dynamic array at that bucket.
            - **Dynamic Rehashing:** When the load factor $\alpha = \frac{n}{m} > 0.75$, the table doubles capacity ($m' = 2m$) and rehashes all elements in $O(n)$ time, ensuring $O(1)$ amortized lookups.
            """
        )

    with st.expander("4. Recommendation Engine & Jaccard Similarity", expanded=True):
        st.markdown(
            r"""
            - **Triadic Closure Principle:** In sociology and network theory, if student $A$ knows $B$, and $B$ knows $C$, there is high likelihood that $A$ and $C$ will connect.
            - **Candidate Generation:** Candidates are discovered exclusively from 2-hop friends-of-friends ($O(d \cdot \bar{k})$), avoiding expensive full-network scans ($O(|V| \cdot d)$).
            - **Jaccard Similarity Score:**
              $$J(A, B) = \frac{|\text{Interests}(A) \cap \text{Interests}(B)|}{|\text{Interests}(A) \cup \text{Interests}(B)|}$$
            - **Hybrid Ranking Strategy:**
              1. Mutual Friends Count (Primary)
              2. Jaccard Similarity of Interests (Secondary)
              3. Alphabetical tie-break
            """
        )

    with st.expander("5. Connected Components & NetworkX Academic Role", expanded=False):
        st.markdown(
            r"""
            - **Connected Components via BFS:** By initiating BFS from unvisited nodes, we partition the campus into distinct connected components and isolated nodes in $O(V + E)$ time without third-party libraries.
            - **Role of NetworkX:** NetworkX is utilized **strictly as an independent automated oracle** to verify our manual BFS distance via `nx.shortest_path_length`, and for layout coordinates in visual rendering. The actual results presented to the user are 100% computed by our manual algorithms.
            """
        )

# -----------------------------------------------------------------------------
# TAB 2: Interactive Viva Quiz
# -----------------------------------------------------------------------------
with tab_quiz:
    st.subheader("🎯 Test Your Viva Voce Readiness")
    st.caption("Interactive quiz covering core questions frequently asked by external examiners.")

    quiz_questions = [
        {
            "q": "1. Why does Breadth-First Search (BFS) guarantee the shortest path in an unweighted graph, but not in a weighted graph?",
            "options": [
                "Because BFS expands nodes in FIFO level-order where path length equals edge count, whereas weighted graphs require Dijkstra's algorithm.",
                "Because BFS uses a stack which processes nodes in reverse depth order.",
                "Because BFS examines fewer edges than depth-first search.",
                "Because BFS only works on directed acyclic graphs (DAGs).",
            ],
            "correct": 0,
            "explanation": "In an unweighted graph, all edges have weight 1. The FIFO queue guarantees nodes are dequeued in monotonically non-decreasing distance order. In a weighted graph, a path with more hops could have a lower total edge weight, requiring a priority queue (Dijkstra).",
        },
        {
            "q": "2. What is the Space Complexity of an Adjacency List for a graph with V vertices and E undirected edges?",
            "options": [
                "O(V^2)",
                "O(V + 2E) which simplifies to O(V + E)",
                "O(E log V)",
                "O(1)",
            ],
            "correct": 1,
            "explanation": "The adjacency list maintains |V| dictionary keys and stores each undirected edge twice (once in each endpoint's set), taking O(V + 2E) = O(V + E) space. An adjacency matrix takes O(V^2).",
        },
        {
            "q": "3. What is the Load Factor (α) in a hash table, and why is 0.75 a standard threshold for rehashing?",
            "options": [
                "α = capacity / size; it measures memory wastage.",
                "α = size / capacity; 0.75 strikes an optimal trade-off between O(1) time and memory overhead.",
                "α = number of collisions; 0.75 means 75% of keys collided.",
                "α is the hash prime multiplier.",
            ],
            "correct": 1,
            "explanation": "Load Factor α = n / m (items / buckets). When α > 0.75, chain lengths grow, degrading average lookup time toward O(n). Doubling capacity keeps average chain length bounded by O(1).",
        },
        {
            "q": "4. How is Jaccard Similarity defined between student interest sets A and B?",
            "options": [
                "J(A, B) = |A ∩ B| / |A ∪ B|",
                "J(A, B) = |A ∪ B| / |A ∩ B|",
                "J(A, B) = |A| * |B|",
                "J(A, B) = |A - B|",
            ],
            "correct": 0,
            "explanation": "Jaccard similarity is the size of the intersection divided by the size of the union of the two sets, ranging from 0.0 (completely disjoint) to 1.0 (identical).",
        },
        {
            "q": "5. What mathematical lemma proves that the sum of degrees of all vertices equals 2 * |E|?",
            "options": [
                "Kuratowski's Theorem",
                "Handshaking Lemma",
                "Euler's Formula",
                "Four Color Theorem",
            ],
            "correct": 1,
            "explanation": "The Handshaking Lemma states that in any undirected graph, every edge has two endpoints, so each edge contributes exactly 2 to the sum of the degrees of the vertices.",
        },
        {
            "q": "6. Why is 2-hop candidate exploration faster than scanning all non-friends in a large social network?",
            "options": [
                "Because scanning 2-hop friends explores O(d * k_avg) neighbors, while scanning the whole graph takes O(|V| * d) where |V| >> d.",
                "Because 2-hop traversal uses Dijkstra's algorithm.",
                "Because NetworkX optimizes the search in C.",
                "Because sorting mutual friends is O(1).",
            ],
            "correct": 0,
            "explanation": "In large networks with millions of users, inspecting friends-of-friends is local and bounded by degree, whereas comparing a user against every member in the network scales with total population |V|.",
        },
    ]

    for item_idx, item in enumerate(quiz_questions):
        with st.container(border=True):
            st.markdown(f"**{item['q']}**")
            choice = st.radio(
                "Select your answer:",
                options=item["options"],
                key=f"quiz_radio_{item_idx}",
                label_visibility="collapsed",
            )
            selected_idx = item["options"].index(choice)

            if st.button("Check Answer", key=f"quiz_btn_{item_idx}"):
                if selected_idx == item["correct"]:
                    st.success(f"✅ **Correct!** {item['explanation']}")
                else:
                    st.error(f"❌ **Incorrect.** Correct answer: *{item['options'][item['correct']]}*")
                    st.info(f"**Explanation:** {item['explanation']}")

# -----------------------------------------------------------------------------
# TAB 3: Complexity Matrix
# -----------------------------------------------------------------------------
with tab_complexities:
    st.subheader("⚡ Complete Algorithmic Complexity Table")

    st.markdown(
        r"""
        | Operation / Algorithm | Module | Time Complexity (Average) | Time Complexity (Worst) | Space Complexity |
        |---|---|---|---|---|
        | **Add Student Node** | `core/graph.py` | $O(1)$ | $O(V)$ (collision) | $O(1)$ |
        | **Add Friendship Edge** | `core/graph.py` | $O(1)$ | $O(1)$ | $O(1)$ |
        | **Remove Student Node** | `core/graph.py` | $O(\deg(u))$ | $O(V)$ | $O(1)$ |
        | **Are Friends Check** | `core/graph.py` | $O(1)$ | $O(\deg(u))$ | $O(1)$ |
        | **Connected Components** | `core/graph.py` | $O(V + E)$ | $O(V + E)$ | $O(V)$ |
        | **BFS Shortest Connection**| `core/bfs.py` | $O(V + E)$ | $O(V + E)$ | $O(V)$ |
        | **BFS Degree Levels** | `core/bfs.py` | $O(V + E)$ | $O(V + E)$ | $O(V)$ |
        | **HashTable Put / Get** | `core/hash_table.py` | $O(1)$ | $O(n)$ (all collide) | $O(1)$ |
        | **HashTable Resize/Rehash**| `core/hash_table.py` | $O(n)$ | $O(n)$ | $O(n)$ |
        | **2-Hop Candidate Search**| `core/recommendation.py` | $O(\sum_{f} \deg(f) + C \log C)$ | $O(E + C \log C)$ | $O(C)$ |
        | **Jaccard Similarity** | `core/recommendation.py` | $O(|A| + |B|)$ | $O(|A| + |B|)$ | $O(|A| + |B|)$ |
        """
    )
