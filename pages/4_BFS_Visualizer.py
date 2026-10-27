"""Interactive BFS Step-by-Step Traversal Visualizer."""

import streamlit as st
from ui.state import get_user_manager, get_social_graph, init_session_state
from ui.styles import apply_custom_styles
from ui.components import render_interactive_graph
from core.bfs import bfs_steps
from core.user_manager import display_name

init_session_state()
apply_custom_styles()

um = get_user_manager()
graph = get_social_graph()

st.title("🚶 Breadth-First Search (BFS) Visualizer")
st.caption("Step-by-step interactive inspection of queue transitions, visited sets, predecessor pointers, and layer expansion.")

all_users = um.get_all_users()
if len(all_users) < 2:
    st.warning("At least 2 students are required for BFS visualizer. Add more in **Network Editor & Data**!")
    st.stop()

def u_sort_key(u):
    uid = str(u["id"])
    return (0, int(uid), uid) if uid.isdigit() else (1, 0, uid)

all_users.sort(key=u_sort_key)
user_options = {u["id"]: f"{u['name']} (@{u.get('username', u['id'])}) — {u.get('branch', 'CSE')}" for u in all_users}
user_id_list = [u["id"] for u in all_users]

# Selector Row
col_s1, col_s2 = st.columns(2)
with col_s1:
    v_src = st.selectbox(
        "Source Student:",
        options=user_id_list,
        index=0,
        format_func=lambda uid: user_options.get(uid, uid),
        key="vis_src_select",
    )
with col_s2:
    v_dst_default = 1 if len(user_id_list) > 1 else 0
    v_dst = st.selectbox(
        "Target Student:",
        options=user_id_list,
        index=v_dst_default,
        format_func=lambda uid: user_options.get(uid, uid),
        key="vis_dst_select",
    )

# Manage BFS Visualizer cached step list
curr_params = (v_src, v_dst)
if "last_vis_params" not in st.session_state or st.session_state.last_vis_params != curr_params:
    st.session_state.last_vis_params = curr_params
    st.session_state.vis_steps_list = list(bfs_steps(graph, v_src, v_dst))
    st.session_state.vis_curr_idx = 0

steps = st.session_state.vis_steps_list
total_steps = len(steps)
curr_idx = st.session_state.vis_curr_idx

# Visualizer Controls
btn_col1, btn_col2, btn_col3, btn_col4, btn_col5 = st.columns([1, 1, 1, 1, 1.5])
with btn_col1:
    if st.button("⏮ Reset", use_container_width=True):
        st.session_state.vis_curr_idx = 0
        st.rerun()
with btn_col2:
    if st.button("◀ Back", disabled=(curr_idx <= 0), use_container_width=True):
        st.session_state.vis_curr_idx = max(0, curr_idx - 1)
        st.rerun()
with btn_col3:
    if st.button("Next ▶", disabled=(curr_idx >= total_steps - 1), type="primary", use_container_width=True):
        st.session_state.vis_curr_idx = min(total_steps - 1, curr_idx + 1)
        st.rerun()
with btn_col4:
    if st.button("⏭ Jump End", disabled=(curr_idx >= total_steps - 1), use_container_width=True):
        st.session_state.vis_curr_idx = total_steps - 1
        st.rerun()
with btn_col5:
    slider_val = st.slider(
        "Step Timeline",
        min_value=0,
        max_value=total_steps - 1,
        value=curr_idx,
        key="step_slider",
        label_visibility="collapsed",
    )
    if slider_val != curr_idx:
        st.session_state.vis_curr_idx = slider_val
        st.rerun()

# Current Step State
step_data = steps[curr_idx]
step_num = step_data["step"]
active_node = step_data["current"]
queue_nodes = step_data["queue"]
visited_nodes = step_data["visited"]
parent_map = step_data["parent"]
level_map = step_data["level"]
is_found = step_data["found"]
narrative = step_data["message"]
final_path = step_data.get("path")

# Narration Bar
st.markdown(
    f"""
    <div class="cc-narration-box">
        <strong>Step {step_num} of {total_steps - 1}:</strong> {narrative}
    </div>
    """,
    unsafe_allow_html=True,
)

# Build Node Color Overrides for Graph Frame
color_overrides: dict[str, str] = {}
for u in graph.get_all_users():
    if final_path and u in final_path:
        color_overrides[u] = "#FF5722"  # Highlighted path
    elif active_node and u == active_node:
        color_overrides[u] = "#E11D48"  # Current dequeued
    elif u in queue_nodes:
        color_overrides[u] = "#F59E0B"  # In FIFO Queue
    elif u in visited_nodes:
        color_overrides[u] = "#10B981"  # Visited
    else:
        color_overrides[u] = "#94A3B8"  # Unvisited

# Side-by-side: Left = Panels, Right = Interactive Graph
col_left, col_right = st.columns([1, 1.2])

with col_left:
    st.subheader("📊 Data Structure State")

    # Panel 1: FIFO Queue
    with st.container(border=True):
        st.markdown(f"**1. FIFO Queue (`collections.deque`)** — [{len(queue_nodes)} item(s)]")
        if queue_nodes:
            q_display = " ➔ ".join(f"`{display_name(um, q)}`" for q in queue_nodes)
            st.markdown(f"**Front (pop):** {q_display} **(push) :Back**")
        else:
            st.markdown("*Queue is currently empty.*")

    # Panel 2: Visited Set
    with st.container(border=True):
        st.markdown(f"**2. Visited Set (`set`)** — [{len(visited_nodes)} visited]")
        if visited_nodes:
            v_names = sorted([display_name(um, v) for v in visited_nodes])
            st.markdown(f"`{', '.join(v_names)}`")
        else:
            st.markdown("*No nodes visited yet.*")

    # Panel 3: Parent Map
    with st.container(border=True):
        st.markdown(f"**3. Parent / Predecessor Map (`dict`)** — [{len(parent_map)} pointer(s)]")
        if parent_map:
            p_items = [f"`{display_name(um, c)}` ➔ `{display_name(um, p)}`" for c, p in parent_map.items()]
            st.markdown(" • ".join(p_items[:12]))
            if len(p_items) > 12:
                st.caption(f"*... and {len(p_items) - 12} more pointers*")
        else:
            st.markdown("*Root source node has no parent.*")

    # Panel 4: Level / Distance Map
    with st.container(border=True):
        st.markdown(f"**4. Distance Levels (`level[u]`)**")
        if level_map:
            l_items = [f"`{display_name(um, u)}`: **{d}**" for u, d in sorted(level_map.items(), key=lambda x: (x[1], x[0]))]
            st.markdown(" • ".join(l_items[:10]))
        else:
            st.markdown("*No distances computed.*")

with col_right:
    st.subheader("🗺️ Live Graph State")

    # Custom mini legend
    st.markdown(
        """
        <div style="display: flex; gap: 10px; font-size: 12px; margin-bottom: 8px;">
            <div><span style="color: #E11D48;">●</span> Dequeued (Active)</div>
            <div><span style="color: #F59E0B;">●</span> In FIFO Queue</div>
            <div><span style="color: #10B981;">●</span> Visited</div>
            <div><span style="color: #94A3B8;">●</span> Unvisited</div>
            <div><span style="color: #FF5722;">●</span> Final Shortest Path</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_interactive_graph(
        graph=graph,
        user_manager=um,
        selected_user=None,
        recommended_users=None,
        path_nodes=final_path,
        node_color_override=color_overrides,
        height="500px",
    )
