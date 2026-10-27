"""Connection Explorer & Shortest Path Finder (BFS) Page."""

import streamlit as st
from ui.state import get_user_manager, get_social_graph, init_session_state
from ui.styles import apply_custom_styles
from ui.components import (
    render_color_legend,
    render_path_chain,
    render_interactive_graph,
    get_avatar_initials,
)
from core.bfs import find_shortest_connection, bfs_levels, verify_with_networkx
from core.user_manager import display_name

init_session_state()
apply_custom_styles()

um = get_user_manager()
graph = get_social_graph()

st.title("🔍 Connection Path Finder")
st.caption("Unweighted Shortest Path & Degrees of Separation using Pure-Python Breadth-First Search (BFS)")

all_users = um.get_all_users()
if len(all_users) < 2:
    st.warning("At least 2 students are required to explore connection paths. Add more in **Network Editor & Data**!")
    st.stop()

def u_sort_key(u):
    uid = str(u["id"])
    return (0, int(uid), uid) if uid.isdigit() else (1, 0, uid)

all_users.sort(key=u_sort_key)
user_options = {u["id"]: f"{u['name']} (@{u.get('username', u['id'])}) — {u.get('branch', 'CSE')}" for u in all_users}
user_id_list = [u["id"] for u in all_users]

# Selection dropdowns with default non-equal target
col_p1, col_p2 = st.columns(2)

current_active = st.session_state.get("active_user_id")
start_default_idx = user_id_list.index(current_active) if current_active in user_id_list else 0
target_default_idx = (start_default_idx + 1) % len(user_id_list)

with col_p1:
    start_uid = st.selectbox(
        "Source Student (From):",
        options=user_id_list,
        index=start_default_idx,
        format_func=lambda uid: user_options.get(uid, uid),
        key="pf_start_select",
    )
    st.session_state.active_user_id = start_uid

with col_p2:
    target_uid = st.selectbox(
        "Destination Student (To):",
        options=user_id_list,
        index=target_default_idx,
        format_func=lambda uid: user_options.get(uid, uid),
        key="pf_target_select",
    )

find_clicked = st.button("🚀 Calculate Shortest Connection Path", type="primary", use_container_width=True)

if find_clicked:
    path, dist = find_shortest_connection(graph, start_uid, target_uid)
    st.session_state.bfs_path = path
    st.session_state.bfs_distance = dist
    st.session_state.bfs_start = start_uid
    st.session_state.bfs_target = target_uid

# Check if BFS results are stored in session
if st.session_state.get("bfs_path") is not None:
    path = st.session_state.bfs_path
    dist = st.session_state.bfs_distance
    s_name = display_name(um, st.session_state.bfs_start)
    t_name = display_name(um, st.session_state.bfs_target)

    st.markdown("---")

    if dist == 0:
        st.info(f"👤 **Identical Student:** {s_name} is the same student as {t_name}. Distance: **0 hops**.")
    elif dist > 0:
        # Verified badge with NetworkX oracle
        is_verified = verify_with_networkx(graph, st.session_state.bfs_start, st.session_state.bfs_target)

        res_col1, res_col2 = st.columns([3, 1])
        with res_col1:
            st.subheader(f"✨ Connection Established: {dist} Degree{'s' if dist != 1 else ''} of Separation")
        with res_col2:
            if is_verified:
                st.markdown('<div style="text-align: right; padding-top: 10px;"><span class="cc-badge cc-badge-verified">✔ Verified with NetworkX</span></div>', unsafe_allow_html=True)

        # Visual path chain
        render_path_chain(um, path)

        # Step-by-step table
        with st.expander("📋 Hop-by-Hop Friendship Traversal Breakdown", expanded=False):
            for i in range(len(path) - 1):
                u_curr = path[i]
                u_next = path[i + 1]
                name_curr = display_name(um, u_curr)
                name_next = display_name(um, u_next)
                st.markdown(
                    f"- **Hop {i + 1}:** **{name_curr}** (ID: `{u_curr}`) ➔ directly friends with ➔ **{name_next}** (ID: `{u_next}`)"
                )
    else:
        st.error(
            f"❌ **No Connection Path Exists:** **{s_name}** and **{t_name}** belong to different, "
            "disconnected components of the campus network. In graph theory, distance = $\\infty$."
        )

# Render Graph highlighting path
st.markdown("---")
st.subheader("🗺️ Connection Graph Visualization")
render_color_legend(include_path=True, include_recommended=False)

render_interactive_graph(
    graph=graph,
    user_manager=um,
    selected_user=start_uid,
    recommended_users=None,
    path_nodes=st.session_state.get("bfs_path"),
    height="540px",
)

st.markdown("---")

# LinkedIn-Style Degrees of Network Breakdown
st.subheader(f"🌐 Network Circles Around {display_name(um, start_uid)}")
st.caption("Computed via level-order BFS traversal (1st, 2nd, and 3rd degree connections).")

levels = bfs_levels(graph, start_uid)

if not levels:
    st.info(f"**{display_name(um, start_uid)}** has no connections in the network.")
else:
    col_l1, col_l2, col_l3 = st.columns(3)

    def render_level_column(col, level_num, level_title, uids):
        with col:
            with st.container(border=True):
                st.markdown(f"**{level_title}** ({len(uids)})")
                if not uids:
                    st.caption("No students at this level.")
                else:
                    for uid in uids[:8]:
                        name = display_name(um, uid)
                        rec = um.get_user(uid)
                        branch = rec.get("branch", "") if rec else ""
                        st.markdown(f"- 👤 {name} *({branch})*")
                    if len(uids) > 8:
                        st.caption(f"*... and {len(uids) - 8} more students*")

    render_level_column(col_l1, 1, "1st Degree (Direct Friends)", levels.get(1, []))
    render_level_column(col_l2, 2, "2nd Degree (Friends of Friends)", levels.get(2, []))
    extended = []
    for d in sorted(levels.keys()):
        if d >= 3:
            extended.extend(levels[d])
    render_level_column(col_l3, 3, "3rd+ Degree (Extended Network)", extended)
