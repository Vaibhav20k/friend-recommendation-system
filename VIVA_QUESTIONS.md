# Master Viva-Voce Examination Guide: Smart Friend Recommendation System

> **College Mini-Project Comprehensive Study & Viva Preparation Guide**  
> **Topic**: Graph Data Structures, Breadth-First Search (BFS), Hash Tables, and Recommendation Algorithms  
> **Course**: Data Structures & Algorithms (CS / IT / AI / DS)

---

## Table of Contents
1. [Section 1: Graph Theory Fundamentals](#section-1-graph-theory-fundamentals)
2. [Section 2: Graph Representation & Hashing](#section-2-graph-representation--hashing)
3. [Section 3: Friend Recommendation Engine](#section-3-friend-recommendation-engine)
4. [Section 4: Breadth-First Search (BFS) Deep Dive](#section-4-breadth-first-search-bfs-deep-dive)
5. [Section 5: System Architecture & Persistence](#section-5-system-architecture--persistence)
6. [Section 6: Common Viva Trap Questions & Model Answers](#section-6-common-viva-trap-questions--model-answers)
7. [Section 7: Real-World Industry Comparisons](#section-7-real-world-industry-comparisons)
8. [Quick Revision Summary Sheet](#quick-revision-summary-sheet)

---

## Section 1: Graph Theory Fundamentals

### 1.1 Formal Definition of a Graph
A graph $G$ is a non-linear data structure defined formally as an ordered pair:
$$G = (V, E)$$
Where:
- **$V$ (Vertices / Nodes)**: A non-empty set of vertices $\{v_1, v_2, \dots, v_n\}$ representing entities. The number of vertices $|V|$ is called the **order** of the graph.
- **$E$ (Edges / Links)**: A set of pairs of vertices $\{(u, v) \mid u, v \in V\}$ representing relationships or interactions between entities. The number of edges $|E|$ is called the **size** of the graph.

```
      (Vertex / Node)
         [ Alice ]
             │
             │  (Edge / Relationship)
             │
         [  Bob  ]
```

### 1.2 Vertices vs. Edges in Social Networks
In modeling a social networking platform:
| Mathematical Component | Social Network Entity | Project Implementation |
|---|---|---|
| **Vertex ($v \in V$)** | A registered user account with attributes (ID, Name, Join Date). | String identifier key in a Python `dict` (e.g., `"1": "Alice"`). |
| **Edge ($e \in E$)** | A friendship or mutual connection between two users. | Elements inside a Python `set` of neighbor IDs. |

### 1.3 Undirected vs. Directed Graphs

#### Undirected Graph (Symmetric Relationship)
In an undirected graph, every edge $(u, v)$ is an unordered pair:
$$(u, v) \equiv (v, u)$$
- **Property**: Symmetry. If $u$ is adjacent to $v$, then $v$ is automatically adjacent to $u$.
- **Real-World Examples**:
  - **Facebook**: When Alice accepts Bob's friend request, Alice is Bob's friend AND Bob is Alice's friend.
  - **LinkedIn**: 1st-degree professional connections are mutual.
- **Project Context**: Our project models friendships as an **undirected graph**. Adding an edge between `"1"` (Alice) and `"2"` (Bob) adds `"2"` to Alice's adjacency set and `"1"` to Bob's adjacency set.

#### Directed Graph / Digraph (Asymmetric Relationship)
In a directed graph, edges are ordered pairs $(u \to v)$ having a distinct direction:
$$(u, v) \ne (v, u)$$
- **Property**: Asymmetry. User $u$ points to $v$, but $v$ does not necessarily point back to $u$.
- **Terminology**:
  - **In-degree ($\text{deg}^-(v)$)**: Number of incoming edges (followers).
  - **Out-degree ($\text{deg}^+(v)$)**: Number of outgoing edges (following).
- **Real-World Examples**:
  - **Twitter / X**: Alice follows Elon Musk, but Elon Musk does not follow Alice.
  - **Instagram**: Alice follows a celebrity account without requiring approval or reciprocity.
  - **Web Page Hyperlinks**: Page A links to Page B, but Page B may not link back.

```
   Undirected (Facebook)                 Directed (Twitter / Instagram)
      [Alice] ─── [Bob]                      [Alice] ───▶ [Celebrity]
  (Alice and Bob are friends)              (Alice follows Celebrity only)
```

### 1.4 Dense vs. Sparse Graphs & Graph Density

#### Maximum Number of Edges
In an undirected simple graph (no self-loops, no parallel edges), the maximum possible number of edges occurs when every vertex is connected to every other vertex (Complete Graph $K_V$):
$$E_{max} = \binom{|V|}{2} = \frac{|V|(|V| - 1)}{2}$$

#### Graph Density Formula ($D$)
Graph density measures the ratio of existing edges to the maximum possible edges:
$$D = \frac{2|E|}{|V|(|V| - 1)}$$
For a directed graph without self-loops:
$$D_{\text{directed}} = \frac{|E|}{|V|(|V| - 1)}$$
- $D = 0$: Empty graph (no edges).
- $D = 1$: Complete graph (every user is connected to every other user).

#### Comparison: Dense vs. Sparse
| Metric / Aspect | Dense Graph | Sparse Graph |
|---|---|---|
| **Edge Count Condition** | $|E| \approx |V|^2$ | $|E| \ll |V|^2$, typically $|E| = O(|V|)$ |
| **Typical Density ($D$)** | Close to $1.0$ ($> 0.5$) | Close to $0.0$ ($< 0.01$) |
| **Preferred Representation** | Adjacency Matrix | Adjacency List |
| **Real-World Occurrence** | Complete mesh networks, all-to-all communications | **Social networks, web graphs, road networks** |

#### Why Real-World Social Networks Are Extremely Sparse
Consider a realistic platform like Facebook or Instagram:
- Number of users $|V| = 10^9$ (1 billion users).
- Maximum possible edges:
  $$E_{max} = \frac{10^9 \times (10^9 - 1)}{2} \approx \frac{10^{18}}{2} = 5 \times 10^{17} \text{ edges}$$
- Average number of friends per active user: $\bar{d} \approx 500$.
- Actual edges:
  $$|E| = \frac{|V| \times \bar{d}}{2} = \frac{10^9 \times 500}{2} = 2.5 \times 10^{11} \text{ edges}$$
- Density:
  $$D = \frac{2 \times (2.5 \times 10^{11})}{10^9 \times 10^9} = \frac{5 \times 10^{11}}{10^{18}} = 0.0000005 = 5 \times 10^{-7}$$
**Conclusion**: Real-world social networks have a density close to $0.00005\%$. They are **overwhelmingly sparse**.

#### Sample Project Density Calculation
In our project's sample dataset (`data/users.json`):
- Vertices $|V| = 12$
- Edges $|E| = 15$
- Maximum possible edges:
  $$E_{max} = \frac{12 \times 11}{2} = 66$$
- Density:
  $$D = \frac{2 \times 15}{12 \times 11} = \frac{30}{132} \approx 0.2273 \quad (22.73\%)$$

---

## Section 2: Graph Representation & Hashing

### 2.1 Adjacency List vs. Adjacency Matrix

```
Adjacency Matrix (12x12 2D Array)            Adjacency List (Dict of Sets)
       1  2  3  4  5 ... 12                   "1": {"2", "3", "4"}
    1 [0, 1, 1, 1, 0 ... 0]                   "2": {"1", "5", "6"}
    2 [1, 0, 0, 0, 1 ... 0]                   "3": {"1", "5", "7"}
    3 [1, 0, 0, 0, 1 ... 0]                   "4": {"1", "6"}
    4 [1, 0, 0, 0, 0 ... 0]                   ...
   ...                                        "12": set()
   12 [0, 0, 0, 0, 0 ... 0]
```

#### Detailed Complexity Comparison Table
| Operation | Adjacency Matrix | Adjacency List (Array / List) | Adjacency List (`dict` of `set`s - Our Project) |
|---|---|---|---|
| **Space Complexity** | $O(V^2)$ | $O(V + E)$ | **$O(V + E)$** |
| **Add Vertex** | $O(V^2)$ (reallocate matrix) | $O(1)$ amortized | **$O(1)$ amortized** |
| **Remove Vertex** | $O(V^2)$ | $O(V + E)$ | **$O(\text{deg}(v))$** |
| **Add Edge $(u, v)$** | $O(1)$ | $O(1)$ | **$O(1)$ average** |
| **Remove Edge $(u, v)$** | $O(1)$ | $O(\text{deg}(u))$ | **$O(1)$ average** |
| **Check Edge $(u, v)$** | $O(1)$ | $O(\text{deg}(u))$ | **$O(1)$ average** |
| **Iterate Neighbors of $u$** | $O(V)$ | $O(\text{deg}(u))$ | **$O(\text{deg}(u))$** |

### 2.2 Why Python `dict` and `set`? Hash Table Mechanics

In this project, the graph is maintained as:
```python
adj_list: dict[str, set[str]] = {
    "1": {"2", "3", "4"},
    "2": {"1", "5", "6"},
    # ...
}
```

#### 1. Hash Table Architecture Under the Hood
Both Python `dict` and `set` are powered by high-performance hash tables:
1. **Hash Function (`__hash__`)**: Converts an arbitrary key (e.g., string `"Alice"`) into a 64-bit integer hash code. Python uses **SipHash-2-4**, which provides uniform distribution and prevents algorithmic complexity attacks (hash collision DoS).
2. **Bucket Index Calculation**:
   $$\text{index} = \text{hash}(\text{key}) \ \& \ (\text{capacity} - 1)$$
   The bitwise AND with mask $(\text{capacity} - 1)$ maps the hash integer into one of the $2^k$ table slots in $O(1)$ CPU cycles.
3. **Collision Resolution (Open Addressing with Perturbation Probing)**:
   - Python does **not** use separate chaining (linked lists at each bucket).
   - Python uses **open addressing** with a pseudo-random perturbation sequence:
     $$j = (5j + 1 + \text{perturb}) \pmod{\text{capacity}}$$
     Where `perturb` is initially shifted down by 5 bits on every collision step. This ensures complete coverage of all slots while avoiding secondary clustering.
4. **Load Factor & Dynamic Resizing**:
   - Load factor $\alpha = \frac{\text{Entries}}{\text{Capacity}}$.
   - When $\alpha > \frac{2}{3} \approx 66.7\%$, Python allocates a new array of $2\times$ or $4\times$ size and re-hashes existing keys.
   - Amortized insertion cost remains $O(1)$.

#### 2. Average vs. Worst-Case Lookup
- **Average Case $O(1)$**: With uniform hash distribution, virtually every user lookup and edge check executes in a single memory dereference.
- **Worst Case $O(N)$**: Occurs only if all keys produce the identical hash bucket index (pathological hash collisions). Python's randomized hash seed (`PYTHONHASHSEED`) makes this impossible in practice.

#### 3. Why `set` is superior to `list` for neighbors
- `v in neighbor_list`: If neighbors are in a Python `list`, checking if user $A$ is friends with user $B$ takes $O(k)$ where $k$ is number of friends (linear scan).
- `v in neighbor_set`: In a Python `set`, checking takes **$O(1)$ average time**.
- **Set Intersection**: Computing mutual friends via `friends[u] & friends[v]` runs in $O(\min(|Friends(u)|, |Friends(v)|))$ time in C-level optimized code.

### 2.3 Memory Trade-offs at Social Network Scale (1 Billion Users)

Suppose an engineer must choose between an Adjacency Matrix and an Adjacency List for a platform with:
- $V = 10^9$ users
- Average degree $\bar{d} = 500$ friends/user

#### Option A: Adjacency Matrix
- Matrix dimensions: $10^9 \times 10^9 = 10^{18}$ cells.
- Even if packed as single bits (1 bit per cell):
  $$\text{Memory} = \frac{10^{18} \text{ bits}}{8 \times 1024^3 \text{ bytes/GB}} \approx 116,415,321 \text{ GB} \approx 116.4 \text{ Petabytes (or } \approx 0.116 \text{ Exabytes)}$$
- **Verdict**: Completely infeasible. No single enterprise server can hold $10^{18}$ bits in RAM.

#### Option B: Adjacency List (Hash-based / Pointers)
- Number of edges: $|E| = \frac{10^9 \times 500}{2} = 2.5 \times 10^{11}$ undirected edges.
- Storing $2 \times |E| = 5 \times 10^{11}$ directed pointers/IDs:
  - At 8 bytes per 64-bit integer ID:
    $$\text{Memory} = 5 \times 10^{11} \times 8 \text{ bytes} \approx 4 \times 10^{12} \text{ bytes} = 4 \text{ TB}$$
- **Verdict**: $4 \text{ TB}$ of graph data fits comfortably in the distributed memory of a small cluster (or a single modern multi-terabyte RAM server like AWS `u-6tb1.56xlarge`).

---

## Section 3: Friend Recommendation Engine

### 3.1 Intuition: Friends-of-Friends & Triadic Closure
The core intuition behind social network friend recommendations is the sociological and graph-theoretic principle of **Triadic Closure**:
> If user $A$ has a strong friendship with $B$, and user $A$ also has a friendship with $C$, there is a heightened probability that $B$ and $C$ know each other or will form an edge in the future.

```
       [ Alice (A) ]
        /         \
       /           \
   [ Bob (B) ] · · · [ Charlie (C) ]
          (Opportunity for Triadic Closure)
```

In our algorithm, a **candidate** for user $u$ is defined as:
> Any user $c$ who is a **friend of a friend** (2 hops away), who is **not yet a direct friend** of $u$, and is **not $u$ themselves**.

### 3.2 Mutual Friends Counting Formula
For any two non-connected users $u$ and $v$, their mutual friends are the intersection of their neighbor sets:
$$\text{Mutual}(u, v) = Friends(u) \cap Friends(v)$$
The recommendation strength / score is the cardinality (size) of this intersection:
$$\text{Score}(u, v) = |\text{Mutual}(u, v)| = |Friends(u) \cap Friends(v)|$$

```python
# Direct mathematical implementation in Python
mutual_friends = graph[u] & graph[v]  # Set intersection
score = len(mutual_friends)
```

### 3.3 Candidate Generation vs. Full-Network Scan

Why don't we just scan all users in the system to calculate recommendations?

```
Approach 1: Full-Network Scan (Naive)
Check EVERY user v in V (1 billion users!) ──────▶ O(|V| * deg(u))  [DISASTROUS]

Approach 2: 2-Hop Candidate Exploration (Smart)
Only inspect friends of direct friends ───────────▶ O(sum_{f in Friends(u)} deg(f)) [OPTIMAL]
```

#### Detailed Comparison
| Strategy | Mechanism | Time Complexity | Real-World Feasibility |
|---|---|---|---|
| **Full-Network Scan** | For a user $u$, iterate over all $v \in V \setminus (Friends(u) \cup \{u\})$ and compute $|Friends(u) \cap Friends(v)|$. | $O(|V| \cdot \text{deg}(u))$ | **Unusable at scale**. If $|V| = 10^9$ and $\text{deg}(u) = 500$, requires 500 billion operations per recommendation call! |
| **2-Hop Candidate Generation** | Traverse only the neighbors of $u$'s friends: $c \in \bigcup_{f \in Friends(u)} Friends(f)$. | $O\left(\sum_{f \in Friends(u)} \text{deg}(f)\right)$ | **Sub-millisecond latency**. Only touches users sharing at least 1 mutual friend. |

### 3.4 Recommendation Ranking and Tie-Breaking

1. **Primary Sort Key**: Mutual Friend Count (Descending).
   - Higher mutual friend count = stronger sociological connection.
2. **Tie-Breaking Rule**:
   - When candidate $A$ and candidate $B$ both have 2 mutual friends, an unambiguous deterministic rule is applied:
     - Alphabetical by user name / lexicographical by User ID (Ascending).
     - Or candidate's global degree / network popularity.

```python
# Python sorting with primary and secondary tie-breaking keys:
# Primary: -mutual_count (descending)
# Secondary: candidate_name (ascending)
ranked_candidates = sorted(
    candidates_data,
    key=lambda item: (-item["mutual_count"], item["name"])
)
```

### 3.5 Time & Space Complexity Analysis

Let:
- $d = |Friends(u)|$ be the degree of the target user $u$.
- $k_f = |Friends(f)|$ be the degree of friend $f \in Friends(u)$.
- $C$ be the total number of unique 2-hop candidate users identified ($C \le \sum_{f} k_f$).

#### Time Complexity Breakdown:
1. **Candidate Extraction**:
   - Iterate over $d$ direct friends: $O(d)$.
   - For each friend $f$, iterate over their friends: $\sum_{f \in Friends(u)} k_f$ operations.
   - Using a hash map counter `candidate_count[c] += 1`: each lookup and increment is $O(1)$ average.
   - Extraction Time: $O\left(\sum_{f \in Friends(u)} \text{deg}(f)\right) = O(d \cdot \bar{k})$.
2. **Filtering**:
   - Discard direct friends $Friends(u)$ and $u$ itself: checking $c \in Friends(u)$ is $O(1)$ via hash set.
3. **Sorting $C$ Candidates**:
   - Python Timsort on $C$ elements takes $O(C \log C)$.
4. **Total Time Complexity**:
   $$\mathbf{T = O\left(\sum_{f \in Friends(u)} \text{deg}(f) + C \log C\right)}$$

#### Space Complexity:
- A hash map or dictionary storing the mutual count and mutual friend sets for $C$ candidates: $O(C)$ space.
- Filter sets: $O(d)$ space.
- Total Auxiliary Space: $\mathbf{O(C + d)}$.

---

## Section 4: Breadth-First Search (BFS) Deep Dive

### 4.1 Why BFS Finds the Shortest Path in Unweighted Graphs
Breadth-First Search systematically visits vertices in **concentric wavefronts (levels)**:
- Level 0: Source node $s$ (distance = 0).
- Level 1: All immediate neighbors of $s$ (distance = 1).
- Level 2: All neighbors of Level 1 nodes that haven't been visited (distance = 2).
- Level $k$: All nodes whose shortest unweighted path from $s$ contains exactly $k$ edges.

```
       Level 0:        [ Source (s) ]
                          /      \
       Level 1:       [ A ]      [ B ]
                     /     \        \
       Level 2:   [ C ]   [ D ]    [ E ]
```

#### Monotonicity Property of the FIFO Queue
The queue in BFS satisfies the invariant that at any moment, the distances of vertices in the queue are non-decreasing:
$$\text{dist}(q_1) \le \text{dist}(q_2) \le \dots \le \text{dist}(q_m) \le \text{dist}(q_1) + 1$$
Because edge weights are uniformly 1 (unweighted):
- No edge can "bypass" a level with a smaller weight.
- The **first time** a target vertex $t$ is dequeued or discovered, it is reached via the minimum number of transitions. Hence, BFS is guaranteed to yield the shortest path.

### 4.2 Role of the FIFO Queue: `collections.deque` vs. `list`

A fundamental viva trap focuses on Python queue data structures!

```
Python list: pop(0) takes O(N) due to memory shifting!
[ Item 0 ][ Item 1 ][ Item 2 ][ Item 3 ]
    ▲
  pop(0) ───▶ Shift Item 1, 2, 3 left by 1 position (O(N) memory copy)

collections.deque: popleft() takes O(1) pointer adjustment!
[ Block 1: Head ] ───▶ [ Block 2 ] ───▶ [ Block 3: Tail ]
    ▲
 popleft() ───▶ Advance head pointer within fixed 64-element memory chunk (O(1))
```

#### Detailed Comparison Table
| Feature | Python `list` as Queue | Python `collections.deque` |
|---|---|---|
| **Underlying C Structure** | Dynamic contiguous array (`PyObject**`) | Doubly-linked list of fixed-size blocks (64 objects/block) |
| **`append(x)` (Enqueue)** | $O(1)$ amortized | $O(1)$ |
| **Dequeue (`pop(0)` vs `popleft()`)** | **$O(N)$ worst & average case** | **$O(1)$ strict constant time** |
| **Reason for Dequeue Cost** | Shifting all $N-1$ remaining pointers left in memory | Simple head pointer increment inside C block |
| **Impact on BFS with $V$ vertices** | Degrades BFS from $O(V+E)$ to **$O(V^2 + E)$** | Retains optimal **$O(V + E)$** |

### 4.3 Role of the `visited` Set
The `visited` set (implemented as a Python `set`) serves two vital functions:
1. **Cycle Prevention**: Social networks contain cycles (e.g., $A-B-C-A$). Without tracking visited nodes, the traversal will oscillate infinitely between neighbors and overflow memory.
2. **Shortest Distance Guarantee**: Ensures that once a vertex is marked visited, we never overwrite its discovered level with a longer alternate path.

### 4.4 Path Reconstruction Using the `parent` Dictionary
BFS computes shortest distances, but to retrieve the actual sequence of vertices (e.g., `["Alice", "Charlie", "Grace", "Ian"]`), we use a **parent pointer dictionary**:
```python
parent: dict[str, str | None] = {source: None}
```

```
Forward BFS:
  Alice explores Charlie  ──▶ parent["Charlie"] = "Alice"
  Charlie explores Grace  ──▶ parent["Grace"] = "Charlie"
  Grace explores Ian      ──▶ parent["Ian"] = "Grace"

Backtracking from Target ("Ian"):
  curr = "Ian"
  curr = parent["Ian"]     ──▶ "Grace"
  curr = parent["Grace"]   ──▶ "Charlie"
  curr = parent["Charlie"] ──▶ "Alice"
  curr = parent["Alice"]   ──▶ None (Stop)

Reversed Path: ["Alice", "Charlie", "Grace", "Ian"]
Degrees of Separation: len(path) - 1 = 3
```

#### Python BFS Path Reconstruction Implementation
```python
from collections import deque

def bfs_shortest_path(graph: dict[str, set[str]], start: str, target: str) -> list[str] | None:
    if start not in graph or target not in graph:
        return None
    if start == target:
        return [start]

    visited = {start}
    queue = deque([start])
    parent = {start: None}

    while queue:
        current = queue.popleft()
        
        if current == target:
            break

        for neighbor in graph[current]:
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                queue.append(neighbor)

    if target not in parent:
        return None  # Disconnected components (e.g., Liam)

    # Backtrack path
    path = []
    curr = target
    while curr is not None:
        path.append(curr)
        curr = parent[curr]
    
    path.reverse()
    return path
```

### 4.5 Complexity Analysis of BFS
- **Time Complexity: $O(V + E)$**
  - Every vertex $v$ is added to `visited` and pushed to the queue at most once: $O(V)$.
  - When dequeued, every outgoing edge $(u, v)$ from $u$ is examined: $\sum_{u \in V} \text{deg}(u) = 2E$ for undirected graph: $O(E)$.
  - Total Time: **$O(V + E)$**.
- **Space Complexity: $O(V)$**
  - Queue holds at most $O(V)$ vertices at any moment.
  - `visited` set holds at most $V$ elements: $O(V)$.
  - `parent` map stores at most $V$ entries: $O(V)$.
  - Total Auxiliary Space: **$O(V)$**.

### 4.6 BFS vs. DFS: Why DFS Fails to Guarantee Shortest Path

```
Graph:
        [ Alice ] ──────── [ David ]
            │                  │
            │                  │
        [ Bob ]   ──────── [ Charlie ]

BFS Traversal from Alice to David:
  Level 1 checks Bob AND David!
  David found immediately at distance 1!
  Shortest Path: [Alice, David] (1 hop)

DFS Traversal from Alice to David:
  DFS chooses arbitrary neighbor first: Alice ──▶ Bob ──▶ Charlie ──▶ David
  Path found: [Alice, Bob, Charlie, David] (3 hops!)
  DFS failed to find the shortest path!
```

#### Key Theoretical Differences
| Feature | Breadth-First Search (BFS) | Depth-First Search (DFS) |
|---|---|---|
| **Traversal Order** | Level-by-level (Wavefront) | Deepest branch first (LIFO) |
| **Data Structure** | FIFO Queue (`collections.deque`) | LIFO Stack (or recursion call stack) |
| **Shortest Path Guarantee** | **Guaranteed** in unweighted graphs | **No guarantee**; finds any arbitrary reachability path |
| **Path Length Optimality** | Finds path with minimum edge count | May return an unnecessarily long path |
| **Best Used For** | Degrees of separation, routing, shortest path | Topological sort, cycle detection, strongly connected components, maze puzzles |

---

## Section 5: System Architecture & Persistence

### 5.1 Four-Layer Architectural Model
The project is built on clean architectural boundaries with a strict **Separation of Concerns (SoC)**:

```
┌────────────────────────────────────────────────────────┐
│               PRESENTATION LAYER (UI)                  │
│   Streamlit Web Interface (app.py)                     │
│   • Sidebar Controls    • User Selection Dropdown       │
│   • Interactive Metrics • Recommendation Cards         │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│              COORDINATION / CONTROLLER                 │
│   • Bridges UI events to core service calls            │
│   • Manages session state and parameter validation     │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│              CORE LOGIC & ALGORITHMS                   │
│   • graph.py           -> Custom Adjacency List        │
│   • recommendation.py  -> Mutual friends calculation   │
│   • bfs.py             -> Shortest path traversal      │
│   • user_manager.py    -> Registry & lookup            │
└─────────────┬────────────────────────────┬─────────────┘
              │                            │
┌─────────────▼──────────────┐ ┌───────────▼─────────────┐
│    DATA PERSISTENCE        │ │   VISUALIZATION LAYER   │
│ • utils/data_handler.py    │ │ • visualization/        │
│ • data/users.json          │ │   graph_visualizer.py   │
│ (JSON Schema validation)   │ │ (NetworkX + Matplotlib) │
└────────────────────────────┘ └─────────────────────────┘
```

### 5.2 Why Algorithms Are Pure Python & NetworkX Is Restricted to Layout

| Layer / Component | Technology Used | Strict Architectural Justification |
|---|---|---|
| **Adjacency List** | Pure Python `dict` & `set` | Demonstrates mastery of core data structures from first principles without relying on high-level library abstractions. |
| **Recommendation Engine** | Pure Python math & set intersection | Custom 2-hop exploration logic and ranking with academic transparency. |
| **Shortest Path & BFS** | Pure Python + `collections.deque` | Manual queue manipulation, cycle prevention, and backtracking. |
| **Graph Drawing** | `networkx` + `matplotlib` | **Visualization ONLY**. Calculating spring layout coordinates (Fruchterman-Reingold algorithm) and rendering nodes/edges onto a canvas. |

> **Viva Golden Rule**: If the examiner asks *"Did you use `nx.shortest_path()` or `nx.common_neighbors()`?"*, your answer must be:  
> **"No sir/ma'am. NetworkX is used exclusively as a rendering pipeline. All algorithms—Adjacency List, Mutual Friends intersection, and BFS shortest path—are implemented manually from scratch in `core/`."**

### 5.3 JSON Serialization & Schema Integrity
Data is persisted in `data/users.json` using human-readable, portable JSON.

#### Data Schema
```json
{
  "users": [
    {"id": "1", "name": "Alice"},
    {"id": "2", "name": "Bob"}
  ],
  "friendships": [
    ["1", "2"],
    ["1", "3"]
  ]
}
```

#### Integrity Invariants Enforced by `data_handler.py`:
1. **Referential Integrity**: Every user ID referenced in the `friendships` array must exist in the `users` array.
2. **Symmetry / Bidirectional Consistency**: When friendship `["1", "2"]` is loaded, edge `"1" -> "2"` and `"2" -> "1"` are inserted.
3. **No Self-Loops**: Friendships where $u = v$ (`["1", "1"]`) are rejected.
4. **Duplicate Prevention**: Friendships are deduplicated using normalized sets `frozenset([u, v])`.

---

## Section 6: Common Viva Trap Questions & Model Answers

### Trap Question 1: "What happens if a user has 0 friends (isolated node)?"
- **Examiner's Angle**: Checking boundary conditions and graph connectivity handling.
- **Punchline Answer**: "The isolated node has degree 0. Candidate extraction returns an empty recommendation list, and BFS returns `None` indicating unreachable components."
- **In-Depth Model Answer**:
  > "In our dataset, **Liam (ID 12)** is an isolated vertex with $\text{deg}(v) = 0$.
  > 1. In `recommendation.py`, the candidate generation loop iterates over the user's friends. Since $Friends(\text{Liam}) = \emptyset$, the loop terminates immediately with 0 iterations, returning an empty recommendation list `[]` without raising errors.
  > 2. In `bfs.py`, if we search for a path between Alice and Liam, BFS exhausts all connected vertices in Alice's component. Liam is never reached or added to the `parent` dictionary. The function detects `target not in parent` and cleanly returns `None` (representing $\infty$ distance / disconnected component)."

---

### Trap Question 2: "Can BFS find the shortest path in a weighted graph? Why or why not?"
- **Examiner's Angle**: Distinguishing between unweighted graphs and weighted graphs (Dijkstra's Algorithm).
- **Punchline Answer**: "No. BFS assumes all edges have equal cost (1 unit). In weighted graphs, a path with fewer edges may have a much higher total weight."
- **In-Depth Model Answer**:
  > "BFS guarantees shortest paths **only when all edge weights are identical (unweighted or uniformly weighted)**. This is because BFS explores strictly by edge count (depth).
  > Consider this counterexample:
  > - Path 1: $A \to B$ with edge weight $10$.
  > - Path 2: $A \to C \to B$ with edge weights $1$ and $2$ (total weight = $3$).
  > BFS would dequeue $B$ directly from $A$ in 1 hop and declare the shortest path to be $A \to B$ (cost 10), failing to find the true lowest-cost path $A \to C \to B$ (cost 3).
  > For non-negatively weighted graphs, **Dijkstra's Algorithm** (using a Min-Priority Queue) must be used. For graphs with negative weights, the **Bellman-Ford Algorithm** is required."

---

### Trap Question 3: "What is the 'Degree of Separation'? What was Milgram's Experiment?"
- **Examiner's Angle**: Testing knowledge of sociological graph theory and real-world networking concepts.
- **Punchline Answer**: "Degree of separation is the shortest path length (number of edges) between two nodes. Milgram proved that any two people on Earth are connected by roughly 6 hops."
- **In-Depth Model Answer**:
  > "The degree of separation between user $u$ and user $v$ is the length of the shortest path connecting them, which equals $\text{number of edges} = \text{number of vertices on path} - 1$.
  > - Direct friends: 1st degree separation (1 hop).
  > - Friends of friends: 2nd degree separation (2 hops).
  > In 1967, social psychologist **Stanley Milgram** conducted the famous **Small-World Experiment**, sending letters across the US via personal acquaintances. He discovered the average path length was approximately **6 hops**, coining the term **'Six Degrees of Separation'**. In 2016, Facebook recalculated this on its global graph of 1.6 billion users and found the average degree of separation had shrunk to **3.57 hops** due to digital connectivity."

---

### Trap Question 4: "Why did you use `collections.deque` instead of a standard Python `list` for the BFS queue?"
- **Examiner's Angle**: Testing CPython memory internals and algorithm complexity.
- **Punchline Answer**: "`list.pop(0)` is an $O(N)$ memory copy operation, whereas `deque.popleft()` is an $O(1)$ pointer modification. Using `list` degrades BFS to $O(V^2 + E)$."
- **In-Depth Model Answer**:
  > "A standard Python `list` is implemented as a contiguous array of pointers. Calling `list.pop(0)` removes the first element, requiring every remaining element to be shifted left in memory by one index, which costs $O(N)$ time per pop. Since BFS performs $V$ pops, using `list` increases the traversal time to $O(V^2 + E)$.
  > In contrast, `collections.deque` is implemented as a doubly-linked list of fixed-size memory blocks (chunks). Calling `deque.popleft()` simply advances a head pointer inside the C structure in strict $O(1)$ constant time, preserving the optimal $O(V + E)$ overall BFS time complexity."

---

### Trap Question 5: "What if there is a cycle in the friendship graph? How does your BFS prevent infinite loops?"
- **Examiner's Angle**: Testing cycle handling and state tracking.
- **Punchline Answer**: "Through the `visited` set. Before enqueuing any neighbor, we check `if neighbor not in visited:`, ensuring each vertex is processed exactly once."
- **In-Depth Model Answer**:
  > "Friendship graphs are naturally cyclic (e.g., Alice $\to$ Bob $\to$ Emma $\to$ Alice forms a 3-cycle).
  > When BFS processes Alice, it enqueues Bob. Later, when Bob is processed, Alice is in Bob's adjacency set.
  > However, because Alice was added to `visited` at the moment of discovery, the condition `if neighbor not in visited:` evaluates to `False`. Alice is ignored and never re-enqueued. Thus, cycles are cleanly handled in $O(1)$ time per check."

---

### Trap Question 6: "What is the time complexity of computing mutual friends using Python set intersection?"
- **Examiner's Angle**: In-depth knowledge of Python built-in operations.
- **Punchline Answer**: "$O(\min(|Friends(u)|, |Friends(v)|))$ average time."
- **In-Depth Model Answer**:
  > "When Python executes `set1 & set2`, it iterates over the **smaller set** and performs an $O(1)$ hash table lookup for each element in the larger set.
  > Therefore, if user $u$ has 10 friends and user $v$ has 1,000 friends, Python only hashes and checks the 10 elements of user $u$. The time complexity is $O(\min(d_u, d_v))$, which is mathematically optimal."

---

### Trap Question 7: "Why didn't you use an Adjacency Matrix if checking an edge is $O(1)$?"
- **Examiner's Angle**: Space complexity vs. lookup complexity trade-off.
- **Punchline Answer**: "An Adjacency Matrix wastes $O(V^2)$ space for sparse social networks, and finding a user's neighbors takes $O(V)$ instead of $O(\text{deg}(u))$."
- **In-Depth Model Answer**:
  > "While an Adjacency Matrix gives $O(1)$ edge checks, it has two fatal flaws for social networks:
  > 1. **Prohibitive Space**: It requires $O(V^2)$ memory. At 1 billion users, that is $10^{18}$ bytes (100+ Petabytes), whereas social networks are 99.99% empty zeros.
  > 2. **Slow Neighbor Retrieval**: To find Alice's friends in a matrix, one must scan the entire row of length $|V|$, costing $O(V)$ time. In our `dict` of `set`s, retrieving Alice's friends takes $O(1)$ time to access the set, and iterating takes $O(\text{deg}(u))$ time, which is orders of magnitude faster when $\text{deg}(u) \ll |V|$."

---

### Trap Question 8: "Can two users have multiple shortest paths between them?"
- **Examiner's Angle**: Multiple paths in unweighted graphs.
- **Punchline Answer**: "Yes. Standard BFS finds one valid shortest path based on traversal order, but all shortest paths share the identical minimum hop count."
- **In-Depth Model Answer**:
  > "Yes. In our dataset, there are two distinct shortest paths of length 2 from Alice to Frank:
  > 1. `Alice -> Bob -> Frank` (Distance = 2)
  > 2. `Alice -> David -> Frank` (Distance = 2)
  > Standard BFS records whichever path discovers Frank first (depending on iteration order of the adjacency set). Both are equally valid shortest paths. To find *all* shortest paths, BFS can be modified to store a list of parents for each node rather than a single parent."

---

### Trap Question 9: "How do you break ties if two candidates have the same number of mutual friends?"
- **Examiner's Angle**: Recommendation ranking algorithms and deterministic sorting.
- **Punchline Answer**: "Using a multi-attribute sorting tuple: primary key is `-mutual_count` (descending), secondary key is `candidate_name` (ascending)."
- **In-Depth Model Answer**:
  > "If Candidate A and Candidate B both have 2 mutual friends with the active user, relying solely on count results in unstable non-deterministic ordering.
  > In our system, we use Python tuple keys: `key=lambda x: (-x['mutual_count'], x['name'])`.
  > If the mutual friend counts are equal, Python evaluates the secondary key lexicographically. In real-world platforms, secondary tie-breakers include interaction frequency, geographical proximity, profile similarity, or global popularity."

---

### Trap Question 10: "What is the difference between Transitive Closure and Triadic Closure?"
- **Examiner's Angle**: Theoretical computer science terminology vs. graph sociology.
- **Punchline Answer**: "Transitive closure connects all reachable pairs at any distance; triadic closure predicts that two nodes with a common neighbor will form an edge."
- **In-Depth Model Answer**:
  > "- **Transitive Closure**: A mathematical relation in graph theory where if path $u \rightsquigarrow w$ exists of any length, edge $(u, w)$ is added (computable via Floyd-Warshall in $O(V^3)$).
  > - **Triadic Closure**: A social network heuristic stating that if $(A, B) \in E$ and $(A, C) \in E$, there is a high likelihood that edge $(B, C)$ will form because $A$ introduces them or provides mutual context."

---

## Section 7: Real-World Industry Comparisons

### 7.1 How Facebook Computes "People You May Know" (PYMK)

At Facebook scale (3+ billion active users), computing recommendations goes far beyond a single-machine 2-hop traversal:

```
┌────────────────────────────────────────────────────────┐
│             FACEBOOK PYMK PIPELINE                     │
│                                                        │
│  1. Candidate Generation (Offline / Batch via MapReduce)│
│     • 2-hop mutual friends graph traversal             │
│     • Contact book synchronization                     │
│     • School / University / Employer affiliations      │
│     ───────────────────────────────                    │
│  2. Feature Extraction (Hundreds of signals)           │
│     • Mutual friend count & mutual friend graph density │
│     • Interaction frequency (likes, comments, tags)    │
│     • Geographic co-location (GPS, Wi-Fi bssid)        │
│     • Graph embeddings (Node2Vec, PyTorch BigGraph)    │
│     ───────────────────────────────                    │
│  3. Real-Time ML Ranking Model                         │
│     • Gradient Boosted Decision Trees (GBDT) + DNNs    │
│     • Predicts P(Friend Request Sent AND Accepted)     │
│     ───────────────────────────────                    │
│  4. Fast Online Serving via TAO                        │
│     • TAO: Facebook's distributed graph data store     │
│     • Caches edges in Memcached layer across clusters  │
└────────────────────────────────────────────────────────┘
```

#### Key Innovations Facebook Uses:
1. **TAO (The Associations and Objects)**: A geographically distributed, write-through caching graph store built on MySQL and Memcached that handles billions of graph edge queries per second.
2. **PyTorch BigGraph (PBG)**: Distributed system for learning continuous vector embeddings of nodes in billion-node graphs. Users with similar embeddings are recommended even without direct mutual friends!

### 7.2 How LinkedIn Displays 1st, 2nd, and 3rd Degree Connections

LinkedIn explicitly reveals the graph traversal depth on every user profile:

```
[ You ] ──(1st Degree)──▶ [ Alice ] ──(2nd Degree)──▶ [ Bob ] ──(3rd Degree)──▶ [ Carol ]
 Direct Connection         Shared Connection           Connection of a 2nd-degree
 (Can message freely)      (Can request intro)         (Out of direct network)
```

#### How LinkedIn Queries Connection Degrees at Scale:
- **Bidirectional BFS (Two-Way Search)**:
  - Standard forward BFS from source $s$ to target $t$ explores $O(b^d)$ nodes, where $b$ is the branching factor (average connections $\approx 400$) and $d$ is depth.
  - At depth $d = 4$, $400^4 = 2.56 \times 10^{10}$ operations!
  - **Bidirectional BFS** runs two simultaneous searches: forward from $s$ and backward from $t$, stopping when the two wavefronts intersect.
  - Complexity drops to $2 \times O(b^{d/2})$. At $d = 4$, $2 \times 400^2 = 320,000$ operations! This is an **$80,000\times$ speedup**.
- **Search Infrastructure**: LinkedIn utilizes a specialized real-time distributed graph search index called **Galene** and **Apache Lucene** extensions to resolve network degrees in sub-10 milliseconds.

---

## Quick Revision Summary Sheet

| Topic / Question | One-Line Summary to Speak in Viva |
|---|---|
| **Graph Definition** | $G = (V, E)$, an ordered pair of vertices (users) and edges (friendships). |
| **Social Graph Type** | Unweighted and undirected (bidirectional friendship symmetry). |
| **Why Adjacency List?** | Social networks are sparse ($|E| \ll |V|^2$). Saves space ($O(V+E)$ vs $O(V^2)$) and gives $O(\text{deg}(u))$ neighbor lookup. |
| **Why `dict` and `set`?** | Uses hash tables for $O(1)$ average-time neighbor lookup, existence checking, and fast set intersection. |
| **Recommendation Heuristic** | 2-hop neighbors (friends of friends) ranked by mutual friend count $|Friends(u) \cap Friends(v)|$. |
| **Why 2-Hop vs All Nodes?** | 2-hop avoids scanning all 1 billion users, focusing only on relevant candidates connected by mutual friends. |
| **Why BFS for Shortest Path?** | Explores level-by-level; the first time target is reached in unweighted graph, it is guaranteed minimal hops. |
| **Why `deque` not `list`?** | `collections.deque.popleft()` is $O(1)$ pointer move; `list.pop(0)` is $O(N)$ memory copy, slowing BFS to $O(V^2)$. |
| **BFS Time & Space** | Time: $O(V + E)$ (visit every vertex and edge once). Space: $O(V)$ (queue, visited, parent). |
| **NetworkX Role** | Exclusively used for UI layout calculation and rendering; all core algorithms are written in pure Python. |
| **Degree of Separation** | Number of edges along the shortest path between two users (proven to be $\approx 3.5$ to 6 in real networks). |
| **Disconnected Node** | Has degree 0; recommendations return `[]`, BFS detects node unreached and returns `None`. |

---
*Created for College Mini-Project Defense and Practical Examination Excellence.*
