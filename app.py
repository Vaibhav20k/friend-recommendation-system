"""Main Streamlit web application for Smart Friend Recommendation System.

Presentation and Controller Layer (Phase 7).
Orchestrates the user interface, manages application state, delegates graph
operations, friend recommendations, BFS shortest path exploration, and
renders NetworkX/Matplotlib visualizations.
"""

from typing import List, Optional
import streamlit as st

from core.graph import SocialGraph
from core.user_manager import UserManager
from core.recommendation import get_friend_recommendations
from core.bfs import find_shortest_connection
from utils.data_handler import DataHandler
from visualization.graph_visualizer import render_social_graph

# -----------------------------------------------------------------------------
# Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Friend Recommendation System",
    layout="wide",
    page_icon="🌐",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# Custom Styling (Modern, Clean Cards, Pills, Metrics)
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Metric Card Styling */
    div[data-testid="stMetric"] {
        background-color: #F8F9FA;
        border: 1px solid #E0E0E0;
        padding: 12px 16px;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    
    /* User Profile & Info Card */
    .user-card {
        background: linear-gradient(135deg, #F5F7FA 0%, #E4E8F0 100%);
        border-radius: 12px;
        padding: 18px 24px;
        border-left: 5px solid #FF7043;
        margin-bottom: 20px;
    }
    
    /* Pill / Badge Styling */
    .badge-pill {
        display: inline-block;
        background-color: #E3F2FD;
        color: #1565C0;
        padding: 4px 12px;
        border-radius: 16px;
        font-weight: 600;
        font-size: 13px;
        margin: 3px 4px 3px 0;
        border: 1px solid #BBDEFB;
    }
    
    .badge-mutual {
        display: inline-block;
        background-color: #E8F5E9;
        color: #2E7D32;
        padding: 3px 10px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 12px;
        margin-right: 6px;
        border: 1px solid #C8E6C9;
    }

    .badge-hop {
        display: inline-block;
        background-color: #FFF3E0;
        color: #E65100;
        padding: 4px 14px;
        border-radius: 16px;
        font-weight: 700;
        font-size: 14px;
        border: 1px solid #FFE0B2;
    }

    /* Recommendation Item Box */
    .rec-box {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
        transition: transform 0.1s ease-in-out;
    }
    .rec-box:hover {
        border-color: #66BB6A;
        box-shadow: 0 4px 8px rgba(0,0,0,0.06);
    }

    /* Path Visualizer Box */
    .path-box {
        background-color: #FAFAFA;
        border: 1px solid #ECEFF1;
        border-left: 5px solid #D32F2F;
        border-radius: 10px;
        padding: 16px 20px;
        margin-top: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Session State Initialization
# -----------------------------------------------------------------------------
def init_session_state() -> None:
    """Load default dataset from data/users.json into session_state if not present."""
    if "user_manager" not in st.session_state or "social_graph" not in st.session_state:
        um, sg = DataHandler.load_network("data/users.json")
        st.session_state.user_manager = um
        st.session_state.social_graph = sg

    if "bfs_path" not in st.session_state:
        st.session_state.bfs_path = None
    if "bfs_distance" not in st.session_state:
        st.session_state.bfs_distance = -1
    if "bfs_start" not in st.session_state:
        st.session_state.bfs_start = None
    if "bfs_target" not in st.session_state:
        st.session_state.bfs_target = None


init_session_state()

user_manager: UserManager = st.session_state.user_manager
social_graph: SocialGraph = st.session_state.social_graph


# -----------------------------------------------------------------------------
# Sidebar: Network Overview, Active User & Graph Management
# -----------------------------------------------------------------------------
st.sidebar.title("🌐 Social Network")

# Reset to Default Button
if st.sidebar.button("🔄 Reset to Default Dataset", use_container_width=True):
    um, sg = DataHandler.load_network("data/users.json")
    st.session_state.user_manager = um
    st.session_state.social_graph = sg
    st.session_state.bfs_path = None
    st.session_state.bfs_distance = -1
    st.session_state.bfs_start = None
    st.session_state.bfs_target = None
    st.sidebar.success("Network reset to default dataset!")
    st.rerun()

st.sidebar.markdown("---")

# Network Metrics
total_users = social_graph.get_user_count()
total_friendships = social_graph.get_friendship_count()
graph_density = (
    (2.0 * total_friendships) / (total_users * (total_users - 1))
    if total_users > 1
    else 0.0
)

st.sidebar.markdown("### 📊 Network Overview")
col_s1, col_s2 = st.sidebar.columns(2)
col_s1.metric("Total Users", total_users)
col_s2.metric("Friendships", total_friendships)
st.sidebar.metric(
    "Graph Density",
    f"{graph_density:.3f}",
    help="Density = 2*E / (V*(V-1)). Measures actual connections vs possible connections.",
)

st.sidebar.markdown("---")

# Collect and sort all users for selectboxes
all_user_records = user_manager.get_all_users()
all_user_records.sort(
    key=lambda u: (0, int(u["id"])) if str(u["id"]).isdigit() else (1, str(u["id"]))
)
user_options = {u["id"]: f"{u['name']} (ID: {u['id']})" for u in all_user_records}
user_id_list = [u["id"] for u in all_user_records]

# Primary User Selection Dropdown
if user_id_list:
    active_user_id = st.sidebar.selectbox(
        "👤 Primary Active User",
        options=user_id_list,
        format_func=lambda uid: user_options.get(uid, f"User {uid}"),
        key="active_user_select",
    )
else:
    active_user_id = None
    st.sidebar.warning("No users in network.")

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Quick Management")

# Management Form 1: Add New User
with st.sidebar.expander("➕ Add New User", expanded=False):
    with st.form("add_user_form", clear_on_submit=True):
        new_uid = st.text_input("New User ID", placeholder="e.g. 13").strip()
        new_name = st.text_input("New User Name", placeholder="e.g. Maya").strip()
        add_user_submit = st.form_submit_button("Add User", use_container_width=True)

        if add_user_submit:
            if not new_uid or not new_name:
                st.error("Both User ID and Name are required.")
            elif user_manager.exists(new_uid) or social_graph.has_user(new_uid):
                st.error(f"User with ID '{new_uid}' already exists.")
            else:
                user_manager.add_user(new_uid, new_name)
                social_graph.add_user(new_uid)
                st.success(f"Added {new_name} (ID: {new_uid})!")
                st.rerun()

# Management Form 2: Add Friendship Edge
with st.sidebar.expander("🤝 Add Friendship", expanded=False):
    if len(user_id_list) >= 2:
        with st.form("add_friendship_form"):
            f_u1 = st.selectbox(
                "User 1",
                options=user_id_list,
                format_func=lambda uid: user_options.get(uid, uid),
                key="add_f_u1",
            )
            f_u2 = st.selectbox(
                "User 2",
                options=user_id_list,
                format_func=lambda uid: user_options.get(uid, uid),
                key="add_f_u2",
            )
            add_f_submit = st.form_submit_button("Connect Users", use_container_width=True)

            if add_f_submit:
                if f_u1 == f_u2:
                    st.error("Cannot create a friendship with oneself.")
                elif social_graph.are_friends(f_u1, f_u2):
                    st.warning("These users are already friends!")
                else:
                    social_graph.add_friendship(f_u1, f_u2)
                    st.success(
                        f"Connected {user_manager.get_user(f_u1)['name']} and "
                        f"{user_manager.get_user(f_u2)['name']}!"
                    )
                    st.rerun()
    else:
        st.info("At least 2 users required to create friendships.")

# Management Form 3: Remove Friendship Edge
with st.sidebar.expander("💔 Remove Friendship", expanded=False):
    if len(user_id_list) >= 2:
        with st.form("remove_friendship_form"):
            rem_u1 = st.selectbox(
                "User 1",
                options=user_id_list,
                format_func=lambda uid: user_options.get(uid, uid),
                key="rem_f_u1",
            )
            rem_u2 = st.selectbox(
                "User 2",
                options=user_id_list,
                format_func=lambda uid: user_options.get(uid, uid),
                key="rem_f_u2",
            )
            rem_f_submit = st.form_submit_button(
                "Remove Friendship", use_container_width=True
            )

            if rem_f_submit:
                if rem_u1 == rem_u2:
                    st.error("Please choose two distinct users.")
                elif not social_graph.are_friends(rem_u1, rem_u2):
                    st.error("These users are not currently friends.")
                else:
                    social_graph.remove_friendship(rem_u1, rem_u2)
                    st.success(
                        f"Removed friendship between {user_manager.get_user(rem_u1)['name']} "
                        f"and {user_manager.get_user(rem_u2)['name']}."
                    )
                    st.rerun()


# -----------------------------------------------------------------------------
# Main Application Header
# -----------------------------------------------------------------------------
st.title("🌐 Smart Friend Recommendation System")
st.caption(
    "A Graph Theory & Breadth-First Search (BFS) Simulation Engine Built From First Principles"
)

# -----------------------------------------------------------------------------
# Tabs Interface
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    [
        "✨ Recommendations & Profile",
        "🔍 Connection Explorer (BFS)",
        "📈 Interactive Network Visualization",
        "📖 How It Works & Theory",
    ]
)

# -----------------------------------------------------------------------------
# TAB 1: Recommendations & Profile
# -----------------------------------------------------------------------------
with tab1:
    if not active_user_id:
        st.info("Please add or select a user from the sidebar.")
    else:
        active_user_data = user_manager.get_user(active_user_id) or {
            "id": active_user_id,
            "name": f"User {active_user_id}",
        }
        active_friends = sorted(
            social_graph.get_friends(active_user_id),
            key=lambda uid: (0, int(uid)) if uid.isdigit() else (1, uid),
        )

        # Active User Profile Card
        st.markdown(
            f"""
            <div class="user-card">
                <h3 style="margin: 0; color: #263238;">👤 {active_user_data['name']}</h3>
                <p style="margin: 4px 0 12px 0; color: #607D8B; font-size: 14px;">
                    <strong>User ID:</strong> <code>{active_user_data['id']}</code> &nbsp;|&nbsp; 
                    <strong>Direct Friends:</strong> {len(active_friends)}
                </p>
                <div>
                    {"".join(f'<span class="badge-pill">🤝 {user_manager.get_user(f)["name"] if user_manager.get_user(f) else f}</span>' for f in active_friends) if active_friends else '<em style="color: #9E9E9E;">No direct friends yet (isolated node).</em>'}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### 🎯 Ranked Friend Recommendations")
        st.caption(
            "Discovered via **2-hop friends-of-friends traversal**, ranked descending by mutual friend count."
        )

        recommendations = get_friend_recommendations(social_graph, active_user_id)

        if not recommendations:
            if not active_friends:
                st.info(
                    f"**{active_user_data['name']}** has no direct friends yet. "
                    "Use the sidebar to add friendships and generate recommendations!"
                )
            else:
                st.info(
                    f"No new friend recommendations found for **{active_user_data['name']}**. "
                    "All friends-of-friends are already direct friends or no 2-hop candidates exist."
                )
        else:
            for rank, rec in enumerate(recommendations, start=1):
                cand_id = rec["user_id"]
                cand_data = user_manager.get_user(cand_id) or {
                    "id": cand_id,
                    "name": f"User {cand_id}",
                }
                cand_name = cand_data["name"]
                mutual_count = rec["mutual_count"]
                mutual_ids = rec["mutual_friends"]
                mutual_names = [
                    user_manager.get_user(m)["name"] if user_manager.get_user(m) else m
                    for m in mutual_ids
                ]

                # Card with details and Add Friend button
                rec_col1, rec_col2 = st.columns([4, 1.2])
                with rec_col1:
                    st.markdown(
                        f"""
                        <div class="rec-box">
                            <div style="display: flex; align-items: center; justify-content: space-between;">
                                <h4 style="margin: 0; color: #1E88E5;">
                                    #{rank} {cand_name} <span style="font-size: 13px; color: #78909C; font-weight: normal;">(ID: {cand_id})</span>
                                </h4>
                                <span class="badge-mutual">⭐ {mutual_count} Mutual Friend{'s' if mutual_count != 1 else ''}</span>
                            </div>
                            <div style="margin-top: 8px; color: #546E7A; font-size: 14px;">
                                <strong>Connected through:</strong> {', '.join(mutual_names)}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with rec_col2:
                    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
                    if st.button(
                        f"➕ Add as Friend",
                        key=f"btn_add_friend_{cand_id}",
                        use_container_width=True,
                    ):
                        social_graph.add_friendship(active_user_id, cand_id)
                        st.success(f"Connected with {cand_name}!")
                        st.rerun()


# -----------------------------------------------------------------------------
# TAB 2: Connection Explorer (BFS)
# -----------------------------------------------------------------------------
with tab2:
    st.markdown("### 🔍 Shortest Connection Explorer")
    st.markdown(
        "Find the **degrees of separation** and exact shortest friendship path between any two users "
        "using level-order Breadth-First Search (BFS)."
    )

    if len(user_id_list) < 2:
        st.warning("At least 2 users are required to explore connections.")
    else:
        col_bfs1, col_bfs2 = st.columns(2)
        with col_bfs1:
            start_user_default_idx = (
                user_id_list.index(active_user_id) if active_user_id in user_id_list else 0
            )
            start_uid = st.selectbox(
                "Select Start User (Source)",
                options=user_id_list,
                index=start_user_default_idx,
                format_func=lambda uid: user_options.get(uid, uid),
                key="bfs_start_select",
            )
        with col_bfs2:
            # Default target to second user if possible
            target_default_idx = 1 if len(user_id_list) > 1 else 0
            target_uid = st.selectbox(
                "Select Destination User (Target)",
                options=user_id_list,
                index=target_default_idx,
                format_func=lambda uid: user_options.get(uid, uid),
                key="bfs_target_select",
            )

        if st.button(
            "🚀 Find Shortest Connection", type="primary", use_container_width=True
        ):
            path, distance = find_shortest_connection(social_graph, start_uid, target_uid)
            st.session_state.bfs_path = path
            st.session_state.bfs_distance = distance
            st.session_state.bfs_start = start_uid
            st.session_state.bfs_target = target_uid

        # Display BFS Result if available
        if st.session_state.bfs_path is not None:
            path = st.session_state.bfs_path
            dist = st.session_state.bfs_distance
            s_name = user_manager.get_user(st.session_state.bfs_start)["name"]
            t_name = user_manager.get_user(st.session_state.bfs_target)["name"]

            if dist == 0:
                st.info(
                    f"**Identical User:** {s_name} is the same as {t_name}. "
                    "Degrees of separation: **0 hops**."
                )
            elif dist > 0:
                path_names = [
                    user_manager.get_user(uid)["name"] if user_manager.get_user(uid) else uid
                    for uid in path
                ]
                formatted_path = " ➔ ".join(
                    f"**{name}**" for name in path_names
                )

                st.markdown(
                    f"""
                    <div class="path-box">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <h4 style="margin: 0; color: #D32F2F;">✨ Connection Established!</h4>
                            <span class="badge-hop">{dist} Degree{'s' if dist != 1 else ''} of Separation</span>
                        </div>
                        <p style="font-size: 16px; margin: 8px 0; color: #263238;">
                            <strong>Shortest Path:</strong> {formatted_path}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.markdown("#### 🚶 Step-by-Step Traversal Breakdown:")
                for step_idx in range(len(path) - 1):
                    u_curr = path[step_idx]
                    u_next = path[step_idx + 1]
                    name_curr = user_manager.get_user(u_curr)["name"]
                    name_next = user_manager.get_user(u_next)["name"]
                    st.write(
                        f"• **Hop {step_idx + 1}:** {name_curr} (ID: `{u_curr}`) "
                        f"is directly friends with {name_next} (ID: `{u_next}`)"
                    )
            else:
                st.error(
                    f"❌ **No Connection Path Exists:** {s_name} and {t_name} belong to "
                    "disconnected components of the network."
                )


# -----------------------------------------------------------------------------
# TAB 3: Interactive Network Visualization
# -----------------------------------------------------------------------------
with tab3:
    st.markdown("### 📈 Interactive Network Visualization")
    st.caption(
        "Powered by NetworkX spring-layout positioning and Matplotlib color-coded highlighting."
    )

    highlight_mode = st.radio(
        "Highlight Mode:",
        options=[
            "Active User & Recommendations",
            "Current BFS Shortest Connection",
            "Neutral Full Network",
        ],
        horizontal=True,
    )

    rec_user_ids = []
    if active_user_id:
        active_recs = get_friend_recommendations(social_graph, active_user_id)
        rec_user_ids = [r["user_id"] for r in active_recs]

    fig = None
    if highlight_mode == "Active User & Recommendations":
        if active_user_id:
            fig = render_social_graph(
                graph=social_graph,
                user_manager=user_manager,
                selected_user=active_user_id,
                recommended_users=rec_user_ids,
                path_nodes=None,
                figsize=(11, 7.5),
            )
        else:
            st.warning("Please select an active user from the sidebar.")
    elif highlight_mode == "Current BFS Shortest Connection":
        if st.session_state.bfs_path and len(st.session_state.bfs_path) >= 2:
            fig = render_social_graph(
                graph=social_graph,
                user_manager=user_manager,
                selected_user=st.session_state.bfs_start,
                recommended_users=None,
                path_nodes=st.session_state.bfs_path,
                figsize=(11, 7.5),
            )
        else:
            st.info(
                "No multi-hop BFS path has been calculated yet. "
                "Go to **Tab 2: Connection Explorer (BFS)** and click **'Find Shortest Connection'**!"
            )
            # Render standard view as fallback
            fig = render_social_graph(
                graph=social_graph,
                user_manager=user_manager,
                selected_user=active_user_id,
                recommended_users=rec_user_ids,
                path_nodes=None,
                figsize=(11, 7.5),
            )
    else:  # Neutral Full Network
        fig = render_social_graph(
            graph=social_graph,
            user_manager=user_manager,
            selected_user=None,
            recommended_users=None,
            path_nodes=None,
            figsize=(11, 7.5),
        )

    if fig is not None:
        st.pyplot(fig)


# -----------------------------------------------------------------------------
# TAB 4: How It Works & Theory
# -----------------------------------------------------------------------------
with tab4:
    st.markdown("### 📖 Algorithm Architecture & Theoretical Foundations")
    st.markdown(
        """
        This project models a real-world social network using foundational graph theory and algorithms.
        Here is a breakdown of the core computer science concepts powering this application:
        """
    )

    with st.expander("1. Graph Representation via Adjacency List", expanded=True):
        st.markdown(
            r"""
            - **Mathematical Model:** A social network is modeled as an undirected, unweighted graph 
              $G = (V, E)$, where $V$ is the set of user vertices and $E$ is the set of mutual friendship edges.
            - **Adjacency List Structure:** Stored internally as a Python dictionary of sets (`Dict[str, Set[str]]`):
              ```python
              self._adj = {
                  "1": {"2", "3", "4"},
                  "2": {"1", "5", "6"},
                  ...
              }
              ```
            - **Space Complexity:** $O(V + E)$ vs $O(V^2)$ for an adjacency matrix. In social networks where graphs are sparse ($\text{average degree} \ll |V|$), adjacency lists save gigabytes of memory.
            - **Fast Hash Table Lookups:** Node existence (`v in graph`) and edge verification (`v in graph._adj[u]`) execute in $O(1)$ average time.
            - **Handshaking Lemma:** The sum of degrees across all vertices equals twice the edge count:
              $$\sum_{v \in V} \deg(v) = 2 \times |E|$$
            """
        )

    with st.expander("2. Mutual Friends Recommendation Algorithm", expanded=True):
        st.markdown(
            r"""
            - **Triadic Closure Principle:** In social network theory, if user $A$ is friends with $B$, and $B$ is friends with $C$, there is a heightened probability that $A$ and $C$ will form a connection.
            - **Algorithm Logic:**
              1. Fetch all direct friends: $F = \text{Friends}(u)$.
              2. For each friend $f \in F$, inspect their friends $C_f = \text{Friends}(f)$.
              3. Filter candidates: Exclude the user themselves ($c \neq u$) and existing friends ($c \notin F$).
              4. Count mutual friends via set intersection:
                 $$\text{Score}(c) = |\text{Friends}(u) \cap \text{Friends}(c)|$$
              5. Rank candidates in descending order of mutual friend count, tie-breaking alphabetically.
            - **Computational Complexity:**
              - Traversal: $O(\sum_{f \in F} \deg(f)) \le O(|E|)$
              - Ranking: $O(C \log C)$ where $C$ is the number of 2-hop candidates.
            """
        )

    with st.expander(
        "3. Shortest Connection Path via Breadth-First Search (BFS)", expanded=True
    ):
        st.markdown(
            r"""
            - **Why BFS Guarantees Shortest Path:** BFS explores the network **level by level** (distance 1, distance 2, etc.) using a FIFO queue (`collections.deque`).
            - **Optimality Proof:** Because each friendship edge has an identical weight of 1, the first time the target node is dequeued, the path traversed must have the minimal number of edges.
            - **Cycle Detection & Path Reconstruction:**
              - `visited` set ensures nodes are never processed multiple times, preventing infinite loops.
              - `parent` dictionary stores the predecessor node during discovery, allowing $O(V)$ backtracking from destination back to source.
            - **Time Complexity:** $O(V + E)$ — every reachable vertex is enqueued once, and every incident edge is inspected twice.
            - **Space Complexity:** $O(V)$ auxiliary memory for queue, visited set, and parent map.
            """
        )

    with st.expander("4. Graph Density Metric", expanded=False):
        st.markdown(
            r"""
            - **Formula:**
              $$\text{Density} = \frac{2 \times |E|}{|V| \times (|V| - 1)}$$
            - **Interpretation:** Represents the ratio of actual friendships in the network to the maximum possible friendships if everyone were friends with everyone else.
            - Density ranges from $0.0$ (no edges) to $1.0$ (complete graph $K_n$).
            """
        )
