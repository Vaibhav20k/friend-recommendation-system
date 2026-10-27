# CampusConnect — Who's in Your Network?
### Advanced Campus Social Network Explorer & Friend Recommendation System

[![Python](https://img.shields.io/badge/Python-3.10%2B%20%7C%203.12-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.36%2B%20%7C%201.66-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![PyVis](https://img.shields.io/badge/Visualization-PyVis%20%28Vis.js%29-4CAF50?style=flat)](https://pyvis.readthedocs.io/)
[![Pytest](https://img.shields.io/badge/Tests-149%20Passed-0A9EDC?style=flat&logo=pytest&logoColor=white)](https://pytest.org/)
[![Coverage](https://img.shields.io/badge/Coverage-96%25%20Core-brightgreen?style=flat)](./tests)
[![Status](https://img.shields.io/badge/Project-College%20Capstone%20Mini--Project-success?style=flat)](#)
[![Viva Guide](https://img.shields.io/badge/Viva%20Guide-100%25%20Preparation-orange?style=flat)](./VIVA_QUESTIONS.md)

An interactive, high-performance campus social network graph explorer and peer recommendation engine built from first principles using **Graph Theory, Breadth-First Search (BFS), Separate-Chaining Hash Tables, and Jaccard Similarity Scoring**.

---

## 1. Project Overview

Social networking platforms such as LinkedIn, Instagram, and college campus portals connect thousands of students by modeling their interactions as graphs. A core driver of student networking and discovery is the **Peer Recommendation Engine** ("Students You May Know"), which identifies potential acquaintances based on mutual network connections and shared interest profiles, alongside the **Connection Explorer**, which calculates the exact shortest degrees of separation between any two students.

### Core Academic Computer Science Principles
- **Graph Representation**: An undirected, unweighted graph implemented via an **Adjacency List** using Python's native `dict` of `set`s (`Dict[str, Set[str]]`).
- **Hand-Written Hash Table**: A custom `HashTable` built from scratch in pure Python using **polynomial rolling hashing** and **separate chaining** to demonstrate internal bucket mechanics and indexing.
- **2-Hop Candidate Traversal**: Local neighborhood candidate extraction avoiding expensive full-network scans ($O(\sum \deg(f))$ vs $O(|V| \cdot \bar{d})$).
- **Hybrid Recommendation Ranking**: Ranks candidates primarily by **mutual friend count**, secondarily by **Jaccard Similarity of interests** ($J(A, B) = \frac{|A \cap B|}{|A \cup B|}$), and alphabetically for tie-breaking.
- **Pure-Python Breadth-First Search (BFS)**: Accurate, unweighted shortest connection path discovery and degrees-of-separation calculation using `collections.deque`.
- **LinkedIn-Style Degree Circles**: Level-order BFS grouping into 1st-degree (direct friends), 2nd-degree (mutual friends), and 3rd-degree+ (extended network).
- **Interactive Vis.js Visualization**: Modern interactive physics-based graphs using **PyVis** (drag, zoom, pan, hover tooltips) with a fallback to static Matplotlib exports.
- **Step-by-Step BFS Visualizer**: Interactive pedagogical engine stepping through FIFO queue transitions, visited sets, predecessor pointer maps, and level discoveries with real-time narration.

> 🎓 **Academic Integrity Policy**: All core algorithms—Adjacency List operations, Breadth-First Search, separate-chaining hash table, connected components, and Jaccard recommendation scoring—are **manually implemented in pure Python from first principles**. NetworkX is utilized **strictly as an automated verification oracle** (`verify_with_networkx`) to cross-check manual BFS distances and for spring-layout coordinates during rendering.

---

## 2. System Architecture

The application adopts a **Layered Modular Architecture** adhering to the **Separation of Concerns (SoC)** design principle.

```mermaid
graph TD
    subgraph UI_Layer [Streamlit Multipage Presentation Layer]
        App[app.py: st.navigation & Theme Config]
        P1[pages/1_Dashboard.py: Network Metrics & Top Hubs]
        P2[pages/2_Recommendations.py: 2-Hop + Jaccard Scoring]
        P3[pages/3_Path_Finder.py: BFS Shortest Path & Verification]
        P4[pages/4_BFS_Visualizer.py: Step-by-Step Traversal Lab]
        P5[pages/5_Hash_Lab.py: Custom HashTable & O(1) Benchmark]
        P6[pages/6_Network_Editor.py: Graph Mutation & File Persistence]
        P7[pages/7_Theory_and_Viva.py: DSA Theory & Interactive Quiz]
    end

    subgraph State_UI [UI State & Component Helpers]
        State[ui/state.py: Session State & Caches]
        Styles[ui/styles.py: Light & Dark Theme CSS]
        Comp[ui/components.py: PyVis Graph & Cards]
    end

    subgraph Core_Layer [Core Algorithmic Engine - Pure Python]
        GraphDS[core/graph.py: Adjacency List & Connected Components]
        UserMgr[core/user_manager.py: Student Registry & Indices]
        CustomHT[core/hash_table.py: Hand-Written Hash Table]
        BFSEngine[core/bfs.py: Manual BFS, Degree Levels & Steps]
        RecEngine[core/recommendation.py: 2-Hop + Jaccard Similarity]
    end

    subgraph Persistence_Layer [Data & Serialization]
        DataHandler[utils/data_handler.py: JSON Validation & I/O]
        GenData[data/generate_dataset.py: Synthetic Generator]
        UsersJSON[(data/users.json: 40-Student Campus Graph)]
        SmallJSON[(data/sample_small.json: 12-User Verification Graph)]
    end

    App --> P1 & P2 & P3 & P4 & P5 & P6 & P7
    P1 & P2 & P3 & P4 & P5 & P6 & P7 --> State & Comp & Styles
    State --> UserMgr & GraphDS
    UserMgr --> CustomHT
    Comp --> GraphDS & BFSEngine & RecEngine
    DataHandler <--> UsersJSON & SmallJSON
    GenData --> UsersJSON
```

---

## 3. Multipage Application Tour

The application features 7 specialized pages designed for presentation and viva demonstrations:

| Page | Key Features | Screenshot |
|---|---|---|
| **1. Campus Dashboard** | Total students, friendships, graph density, average degree, connected components, isolated count; interactive full-campus graph; top-5 influencer hubs leaderboard. | `docs/screenshots/1_dashboard.png` |
| **2. Friend Recommendations** | Searchable student picker; student profile card (avatar, branch, year, interest tags); ranked recommendations with mutual friends and Jaccard interest scores; inline "Connect Friend" buttons; 2-hop neighborhood graph. | `docs/screenshots/2_recommendations.png` |
| **3. Connection Path Finder** | Shortest path discovery between any two students; visual avatar breadcrumb chain; degrees-of-separation badge; **✔ Verified with NetworkX** badge; LinkedIn-style 1st/2nd/3rd degree network circle columns. | `docs/screenshots/3_path_finder.png` |
| **4. BFS Step Visualizer** | Interactive pedagogical step-by-step engine; Play/Pause/Step controls; side-by-side view with live-colored graph and data structure state panels: **FIFO Queue**, **Visited Set**, **Parent Map**, and **Current Level**. | `docs/screenshots/4_bfs_visualizer.png` |
| **5. Hash Table Lab** | Live username inspector computing polynomial hash code, bucket index, and bucket chain; bucket distribution bar chart; load factor and collision statistics; **empirical benchmark comparing $O(1)$ HashTable lookup vs $O(N)$ linear list scan**. | `docs/screenshots/5_hash_lab.png` |
| **6. Network Editor & Data** | Register student (auto-generated ID, duplicate handle validation); dissolve/form friendships; save permanently to `data/users.json`; download/upload JSON with schema validation; load synthetic campus graphs ($N = 50, 200, 1000$). | `docs/screenshots/6_network_editor.png` |
| **7. Theory & Viva Guide** | Full mathematical derivations, complexity matrix, handshaking lemma; **interactive viva quiz with 8 frequently asked questions** and instant feedback. | `docs/screenshots/7_theory_and_viva.png` |

---

## 4. Sample Datasets & Verification

### Primary Dataset: CampusConnect 40-Student Graph (`data/users.json`)
The primary dataset models a realistic college campus social network:
- **40 students** across 7 branches (CSE, IT, ECE, ME, CE, EE, AIDS) and study years (1–4) with 2–4 interest tags.
- **116 friendships** forming:
  - A dense core community (CSE coding club).
  - Cross-branch bridges (sports, music, hackathon teams).
  - **1 isolated student** (ID: 40) with 0 connections (demonstrates empty recommendation states).
  - **1 small separate component** (IDs: 38 and 39) connected only to each other (demonstrates BFS unreachable components).

### Canonical 12-User Verification Graph (`data/sample_small.json`)
Retained for academic verification and unit test benchmarking:

```
Alice (1)  ─── Bob (2)   ─── Emma (5)  ─── Hannah (8) ─── Ian (9) ─── Kelly (11)
  │      ＼      │          │                 ＼         ／             │
  │        ＼    │          │                   ＼     ／               │
  │          ＼  │          │                     Grace (7)             │
Charlie (3) ─── David (4) ── Frank (6) ─────────────────────────── Jack (10)

Liam (12) [Isolated Student - 0 Friends]
```

### Pre-computed Verification Matrix (Canonical Graph)
| Metric / Query | Expected Output | Theoretical Significance |
|---|---|---|
| **Alice's Direct Friends** | Bob (2), Charlie (3), David (4) | Level 1 BFS neighbors |
| **Alice's Top Recommendations** | **Emma (5)**: 2 mutual (Bob, Charlie)<br/>**Frank (6)**: 2 mutual (Bob, David)<br/>**Grace (7)**: 1 mutual (Charlie) | 2-hop candidate generation & set intersection |
| **Shortest Path: Alice $\to$ Ian** | `Alice (1) -> Charlie (3) -> Grace (7) -> Ian (9)` (Length: 3 hops) | Level-order BFS shortest path guarantee |
| **Shortest Path: Alice $\to$ Liam** | `None` (Distance: -1) | Disconnected component detection |
| **Network Density** | $D = \frac{2 \times 15}{12 \times 11} \approx 22.73\%$ | Quantifying graph sparsity |

---

## 5. Algorithmic Complexity Reference

| Operation / Algorithm | Implementation Module | Time Complexity (Average) | Time Complexity (Worst) | Space Complexity |
|---|---|---|---|---|
| **Add Student Node** | `core/graph.py` | $O(1)$ | $O(V)$ (hash collision) | $O(1)$ |
| **Add Friendship Edge** | `core/graph.py` | $O(1)$ | $O(1)$ | $O(1)$ |
| **Remove Student Node** | `core/graph.py` | $O(\deg(u))$ | $O(V)$ | $O(1)$ |
| **Are Friends Check** | `core/graph.py` | $O(1)$ | $O(\deg(u))$ | $O(1)$ |
| **Connected Components** | `core/graph.py` | $O(V + E)$ | $O(V + E)$ | $O(V)$ |
| **BFS Shortest Path** | `core/bfs.py` | $O(V + E)$ | $O(V + E)$ | $O(V)$ |
| **BFS Degree Levels** | `core/bfs.py` | $O(V + E)$ | $O(V + E)$ | $O(V)$ |
| **HashTable Put / Get** | `core/hash_table.py` | $O(1)$ | $O(n)$ (all collide) | $O(1)$ |
| **HashTable Rehashing** | `core/hash_table.py` | $O(n)$ | $O(n)$ | $O(n)$ |
| **2-Hop Candidate Search** | `core/recommendation.py` | $O(\sum_{f} \deg(f) + C \log C)$ | $O(E + C \log C)$ | $O(C)$ |
| **Jaccard Similarity** | `core/recommendation.py` | $O(\|A\| + \|B\|)$ | $O(\|A\| + \|B\|)$ | $O(\|A\| + \|B\|)$ |

---

## 6. Installation & Execution Guide

### Prerequisites
- **Python 3.10 to 3.12**
- **Git**

### Installation

#### On Windows (PowerShell):
```powershell
# 1. Clone repository
git clone https://github.com/Vaibhav20k/friend-recommendation-system.git
cd friend-recommendation-system

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
.venv\Scripts\Activate.ps1

# 4. Install dependencies
pip install -r requirements.txt
```

#### On Linux / macOS (Bash):
```bash
# 1. Clone repository
git clone https://github.com/Vaibhav20k/friend-recommendation-system.git
cd friend-recommendation-system

# 2. Create virtual environment
python3 -m venv .venv

# 3. Activate virtual environment
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt
```

---

## 7. Running the Test Suite & Verification

Execute the complete automated test suite with coverage:
```bash
pytest -v --cov=core --cov=utils
```

### Verified Pytest Output
```text
============================= test session starts =============================
platform win32 / linux -- Python 3.12.x, pytest-9.1.1, pluggy-1.7.0
plugins: anyio-4.15.1, cov-7.1.0
collected 149 items

tests/test_bfs.py ...............                                        [ 10%]
tests/test_campus_features.py ...............                            [ 20%]
tests/test_data_handler_features.py ......                               [ 24%]
tests/test_graph.py ........................................             [ 51%]
tests/test_hash_table.py ..........                                      [ 58%]
tests/test_integration.py ....                                           [ 60%]
tests/test_recommendation.py .............                               [ 69%]
tests/test_security_and_negative.py .........................            [ 86%]
tests/test_tdd_feature.py .........                                      [ 92%]
tests/test_ui_smoke.py ........                                          [ 97%]
tests/test_visualization.py .....                                        [100%]

=============================== tests coverage ================================
Name                     Stmts   Miss  Cover
--------------------------------------------
core/__init__.py             6      0   100%
core/bfs.py                115      3    97%
core/graph.py              145      1    99%
core/hash_table.py         117      6    95%
core/recommendation.py      85      4    95%
core/user_manager.py       149     13    91%
utils/__init__.py            2      0   100%
utils/data_handler.py      175     15    91%
--------------------------------------------
TOTAL                      794     42    95%
============================= 149 passed in 18.25s =============================
```

---

## 8. Launching the Web Application

Launch the Streamlit web dashboard:
```bash
streamlit run app.py
```

The application will launch in your default web browser at:
- **Local URL**: `http://localhost:8501`

---

## 9. Repository Structure

```text
friend-recommendation-system/
│
├── app.py                      # Multipage controller & navigation orchestrator
├── requirements.txt            # Pinned dependencies (pyvis, pytest-cov, streamlit...)
├── README.md                   # Project documentation & viva guide
├── VIVA_QUESTIONS.md           # Master viva-voce exam guide with model answers
├── TESTING_AND_SECURITY_REPORT.md # QA and AppSec verification report
│
├── .streamlit/
│   └── config.toml             # Defined light/dark theme specification
│
├── core/                       # Core DSA Algorithms (Pure Python from First Principles)
│   ├── __init__.py
│   ├── graph.py                # Adjacency List & BFS Connected Components
│   ├── user_manager.py         # Student registry & custom HashTable handle lookup
│   ├── hash_table.py           # Custom Separate-Chaining Hash Table & Rehashing
│   ├── bfs.py                  # Shortest Path, Degree Levels, Steps & NX Verification
│   └── recommendation.py       # 2-Hop Traversal & Jaccard Interest Similarity
│
├── ui/                         # Presentation Components & Styles
│   ├── __init__.py
│   ├── state.py                # Session state initialization & cache clearing
│   ├── styles.py               # Theme-adaptive CSS variables (Light + Dark mode)
│   └── components.py           # PyVis interactive graph, student cards, legends
│
├── pages/                      # Multipage Navigation Modules
│   ├── 1_Dashboard.py          # Campus overview, metrics & top hub students
│   ├── 2_Recommendations.py    # Ranked 2-hop + Jaccard recommendation cards
│   ├── 3_Path_Finder.py        # BFS connection path & NetworkX verification badge
│   ├── 4_BFS_Visualizer.py     # Interactive step-by-step traversal with narration
│   ├── 5_Hash_Lab.py           # Custom HashTable inspector & O(1) vs O(N) benchmark
│   ├── 6_Network_Editor.py     # Graph mutation, JSON sync & dataset generation
│   └── 7_Theory_and_Viva.py    # Algorithmic theory & interactive viva exam quiz
│
├── data/                       # Datasets & Generators
│   ├── users.json              # Primary CampusConnect dataset (40 students)
│   ├── sample_small.json       # Canonical 12-user verification dataset
│   └── generate_dataset.py     # Synthetic campus dataset generator (N=50/200/1000)
│
├── visualization/              # Visualization Helpers
│   ├── __init__.py
│   └── graph_visualizer.py     # Fallback Matplotlib graph rendering & PNG export
│
└── tests/                      # Automated Test Suite (149 Tests)
    ├── test_bfs.py
    ├── test_campus_features.py
    ├── test_data_handler_features.py
    ├── test_graph.py
    ├── test_hash_table.py
    ├── test_integration.py
    ├── test_recommendation.py
    ├── test_security_and_negative.py
    ├── test_tdd_feature.py
    ├── test_ui_smoke.py
    └── test_visualization.py
```

---

## 10. License & Academic Attribution
Developed as an advanced academic college project in **Data Structures, Graph Theory & Algorithms**. Free to use and extend for academic and learning purposes.
