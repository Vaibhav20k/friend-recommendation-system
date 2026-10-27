"""Campus Dashboard Page — Overview of Campus Social Graph."""

import streamlit as st
from ui.state import get_user_manager, get_social_graph, init_session_state
from ui.styles import apply_custom_styles
from ui.components import (
    render_color_legend,
    render_interactive_graph,
    render_static_graph_download,
    get_avatar_initials,
)
from core.user_manager import display_name

init_session_state()
apply_custom_styles()

um = get_user_manager()
graph = get_social_graph()

# Header
st.title("🎓 CampusConnect")
st.caption("Campus Social Network Explorer — Graph Theory, Breadth-First Search & Hash Tables")

# Empty State Check
if graph.get_user_count() == 0:
    st.info("The campus network is currently empty. Go to **Network Editor & Data** to load or add students!")
    st.stop()

# Metric Row
metrics = graph.get_network_metrics()
col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Students", metrics["total_users"], help="Total student vertices |V|")
col2.metric("Friendships", metrics["total_friendships"], help="Total unique undirected connections |E|")
col3.metric("Density", f"{metrics['density']:.3f}", help="Actual connections vs maximum possible: 2|E| / (|V|(|V|-1))")
col4.metric("Avg Degree", f"{metrics['average_degree']:.2f}", help="Average connections per student: 2|E| / |V|")
col5.metric("Components", metrics["component_count"], help="Number of disconnected communities")
col6.metric("Isolated", metrics["isolated_count"], help="Students with 0 connections")

st.markdown("---")

# Main Interactive Graph
st.subheader("🌐 Campus Social Network Map")
render_color_legend(include_path=False, include_recommended=False)

render_interactive_graph(
    graph=graph,
    user_manager=um,
    selected_user=st.session_state.get("active_user_id"),
    recommended_users=None,
    path_nodes=None,
    height="580px",
)

# Download Option
with st.expander("📥 Static Matplotlib Graph & Export", expanded=False):
    render_static_graph_download(
        graph=graph,
        user_manager=um,
        selected_user=st.session_state.get("active_user_id"),
    )

st.markdown("---")

# Bottom Highlights: Top Influencers and Disconnected Nodes
col_left, col_right = st.columns([1.2, 1])

with col_left:
    st.subheader("🏆 Most Connected Students (Hubs)")
    adj = graph.get_adjacency_list()
    sorted_by_deg = sorted(
        [(uid, len(nbrs)) for uid, nbrs in adj.items()],
        key=lambda x: (-x[1], int(x[0]) if x[0].isdigit() else x[0]),
    )
    top_5 = sorted_by_deg[:5]

    for rank, (uid, deg) in enumerate(top_5, start=1):
        rec = um.get_user(uid)
        name = rec["name"] if rec else f"User {uid}"
        username = rec.get("username", uid) if rec else uid
        branch = rec.get("branch", "CSE") if rec else "CSE"
        year = rec.get("year", 1) if rec else 1
        initials = get_avatar_initials(name)

        st.markdown(
            f"""
            <div style="display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; background: rgba(148, 163, 184, 0.08); border-radius: 10px; margin-bottom: 8px;">
                <div style="display: flex; align-items: center;">
                    <span style="font-weight: 700; width: 24px; color: #64748B;">#{rank}</span>
                    <div class="cc-avatar" style="width: 34px; height: 34px; font-size: 13px;">{initials}</div>
                    <div>
                        <strong>{name}</strong> <span style="font-size: 12px; color: #64748B;">(@{username})</span>
                        <div style="font-size: 12px; color: #64748B;">{branch} • Year {year}</div>
                    </div>
                </div>
                <div>
                    <span class="cc-badge cc-badge-mutual">🤝 {deg} friends</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

with col_right:
    st.subheader("🏝️ Disconnected / Isolated Students")
    isolated = metrics.get("isolated_users", [])
    components = metrics.get("connected_components", [])
    small_comps = [c for c in components if len(c) > 1 and len(c) < max(len(comp) for comp in components)]

    if isolated:
        st.markdown(f"**Isolated Students (Degree 0):** `{len(isolated)}` student(s)")
        for iso_id in isolated:
            name = display_name(um, iso_id)
            rec = um.get_user(iso_id)
            branch = rec.get("branch", "N/A") if rec else "N/A"
            st.markdown(f"- 👤 **{name}** (ID: `{iso_id}`) — *{branch} Department* (0 friends)")
    else:
        st.info("No completely isolated students in network.")

    if small_comps:
        st.markdown(f"**Separate Island Communities:** `{len(small_comps)}` small component(s)")
        for idx, comp in enumerate(small_comps, start=1):
            names = [display_name(um, cid) for cid in comp]
            st.markdown(f"- **Island #{idx} ({len(comp)} students):** {', '.join(names)}")
    elif len(components) <= 1:
        st.success("The network forms a single connected graph.")
