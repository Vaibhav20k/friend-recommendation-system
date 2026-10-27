"""Reusable UI components for CampusConnect web application.

Provides:
- Interactive PyVis (vis.js) network visualization with fallback to Matplotlib.
- Color legends, avatar chips, metric rows, and student profile cards.
- Consistent visual language across all pages.
"""

from typing import Any, Dict, List, Optional, Set, Tuple
import html
import io
import streamlit as st
import streamlit.components.v1 as components

from core.graph import SocialGraph
from core.user_manager import UserManager, display_name
from visualization.graph_visualizer import render_social_graph


# Color Palette Specification
COLOR_SELECTED = "#FF5722"    # Coral / Deep Orange
COLOR_FRIEND = "#2196F3"      # Sky Blue
COLOR_RECOMMENDED = "#10B981" # Emerald Green
COLOR_PATH = "#F59E0B"        # Amber
COLOR_ISOLATED = "#94A3B8"    # Subtle Slate Grey
COLOR_OTHER = "#64748B"       # Medium Slate
COLOR_EDGE_NORMAL = "rgba(148, 163, 184, 0.45)"
COLOR_EDGE_PATH = "#EF4444"   # Crimson Red (Width: 4)


def get_avatar_initials(name: str) -> str:
    """Generate 1-2 letter initials from a student name."""
    if not name:
        return "?"
    parts = name.strip().split()
    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[1][0]}".upper()
    return parts[0][:2].upper()


def render_color_legend(include_path: bool = True, include_recommended: bool = True) -> None:
    """Render a clean, responsive color legend bar above/below the graph."""
    items = [
        (COLOR_SELECTED, "Selected Student"),
        (COLOR_FRIEND, "Direct Friend (1st-deg)"),
    ]
    if include_recommended:
        items.append((COLOR_RECOMMENDED, "Recommended (2nd-deg)"))
    if include_path:
        items.append((COLOR_PATH, "Shortest Path Node"))
        items.append((COLOR_EDGE_PATH, "Path Edge (Line)"))
    items.append((COLOR_ISOLATED, "Isolated / Other"))

    legend_html = '<div style="display: flex; flex-wrap: wrap; gap: 14px; align-items: center; padding: 10px 14px; background: rgba(148, 163, 184, 0.08); border-radius: 10px; margin-bottom: 12px; font-size: 13px;">'
    for color, label in items:
        if "Line" in label:
            indicator = f'<span style="display: inline-block; width: 22px; height: 4px; background-color: {color}; border-radius: 2px; vertical-align: middle; margin-right: 6px;"></span>'
        else:
            indicator = f'<span style="display: inline-block; width: 14px; height: 14px; border-radius: 50%; background-color: {color}; vertical-align: middle; margin-right: 6px; box-shadow: 0 1px 2px rgba(0,0,0,0.15);"></span>'
        legend_html += f'<div>{indicator}<span>{label}</span></div>'
    legend_html += '</div>'

    st.markdown(legend_html, unsafe_allow_html=True)


def render_student_hero(
    user_manager: UserManager,
    graph: SocialGraph,
    user_id: str,
) -> None:
    """Render a hero profile card for the active student."""
    rec = user_manager.get_user(user_id)
    if not rec:
        st.warning(f"Student ID '{user_id}' not found.")
        return

    name = rec.get("name", f"User {user_id}")
    username = rec.get("username", user_id)
    branch = rec.get("branch", "CSE")
    year = rec.get("year", 1)
    interests = rec.get("interests", [])
    friends = sorted(
        graph.get_friends(user_id),
        key=lambda u: (0, int(u)) if str(u).isdigit() else (1, str(u)),
    )
    initials = get_avatar_initials(name)

    interest_chips = "".join(
        f'<span class="cc-badge cc-badge-interest">🏷️ {html.escape(t)}</span>' for t in interests
    )
    friend_chips = "".join(
        f'<span class="cc-badge cc-badge-branch">🤝 {html.escape(display_name(user_manager, f))}</span>'
        for f in friends
    ) if friends else '<em style="color: #94A3B8;">No direct friends yet (isolated student).</em>'

    hero_html = f"""
    <div class="cc-hero-card">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap;">
            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                <div class="cc-avatar">{initials}</div>
                <div>
                    <h3 style="margin: 0; font-size: 20px; font-weight: 700;">{html.escape(name)}</h3>
                    <div style="font-size: 13px; color: #64748B; margin-top: 2px;">
                        <code>@{html.escape(username)}</code> &nbsp;•&nbsp; ID: <code>{html.escape(user_id)}</code>
                    </div>
                </div>
            </div>
            <div style="margin-bottom: 8px;">
                <span class="cc-badge cc-badge-branch">🎓 {html.escape(branch)}</span>
                <span class="cc-badge cc-badge-year">Year {year}</span>
                <span class="cc-badge cc-badge-mutual">👥 {len(friends)} Friends</span>
            </div>
        </div>
        <div style="margin-top: 10px;">
            <div style="font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; color: #64748B; margin-bottom: 4px;">Interests</div>
            <div>{interest_chips if interest_chips else '<span style="color: #94A3B8;">No interests listed</span>'}</div>
        </div>
        <div style="margin-top: 10px;">
            <div style="font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; color: #64748B; margin-bottom: 4px;">Direct Friends</div>
            <div>{friend_chips}</div>
        </div>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)


def render_path_chain(user_manager: UserManager, path: List[str]) -> None:
    """Render a visual breadcrumb chain of student avatars and hop arrows."""
    if not path:
        return

    chips = []
    for uid in path:
        name = display_name(user_manager, uid)
        rec = user_manager.get_user(uid)
        branch = f" ({rec['branch']})" if rec and "branch" in rec else ""
        chips.append(
            f'<span class="cc-chain-step">👤 {html.escape(name)}{html.escape(branch)}</span>'
        )

    chain_html = f"""
    <div class="cc-path-container">
        <div style="font-size: 13px; font-weight: 700; color: #D97706; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">
            🔗 Connection Chain ({len(path) - 1} Degree{'s' if len(path) - 1 != 1 else ''} of Separation)
        </div>
        <div style="display: flex; flex-wrap: wrap; align-items: center;">
            {'<span class="cc-chain-arrow">➔</span>'.join(chips)}
        </div>
    </div>
    """
    st.markdown(chain_html, unsafe_allow_html=True)


def render_interactive_graph(
    graph: SocialGraph,
    user_manager: UserManager,
    selected_user: Optional[str] = None,
    recommended_users: Optional[List[str]] = None,
    path_nodes: Optional[List[str]] = None,
    focused_subgraph_nodes: Optional[Set[str]] = None,
    height: str = "580px",
    node_color_override: Optional[Dict[str, str]] = None,
) -> None:
    """Render a fully interactive Vis.js (pyvis) network graph with physics and tooltip inspection.

    Args:
        graph: The SocialGraph instance.
        user_manager: UserManager instance for profile attributes.
        selected_user: Optional focal student ID.
        recommended_users: Optional list of recommended student IDs.
        path_nodes: Optional list of student IDs representing BFS shortest path.
        focused_subgraph_nodes: Optional subset of node IDs to restrict rendering to.
        height: CSS height of graph frame.
        node_color_override: Optional mapping {user_id: color} (used by BFS visualizer).
    """
    try:
        from pyvis.network import Network

        net = Network(height=height, width="100%", bgcolor="transparent", font_color="#1E293B")
        net.barnes_hut(gravity=-3000, central_gravity=0.3, spring_length=120, spring_strength=0.04, damping=0.09)

        rec_set = set(recommended_users) if recommended_users else set()
        path_set = set(path_nodes) if path_nodes else set()
        path_edges_set = set()
        if path_nodes and len(path_nodes) >= 2:
            for i in range(len(path_nodes) - 1):
                u, v = path_nodes[i], path_nodes[i + 1]
                path_edges_set.add((min(u, v), max(u, v)))

        direct_friends = graph.get_friends(selected_user or "")

        # Determine which nodes to render
        all_nodes = graph.get_all_users()
        if focused_subgraph_nodes:
            all_nodes = all_nodes.intersection(focused_subgraph_nodes)

        def node_key(u: str) -> Tuple[int, int, str]:
            return (0, int(u), u) if u.isdigit() else (1, 0, u)

        sorted_nodes = sorted(all_nodes, key=node_key)

        for node_id in sorted_nodes:
            deg = graph.degree(node_id)
            rec = user_manager.get_user(node_id)
            name = rec["name"] if rec else f"User {node_id}"
            branch = rec.get("branch", "CSE") if rec else "CSE"
            year = rec.get("year", 1) if rec else 1
            interests = ", ".join(rec.get("interests", [])) if rec else "None"
            username = rec.get("username", node_id) if rec else node_id

            # Color logic
            if node_color_override and node_id in node_color_override:
                color = node_color_override[node_id]
            elif selected_user and node_id == selected_user:
                color = COLOR_SELECTED
            elif path_nodes and node_id in path_set:
                color = COLOR_PATH
            elif node_id in direct_friends:
                color = COLOR_FRIEND
            elif node_id in rec_set:
                color = COLOR_RECOMMENDED
            elif deg == 0:
                color = COLOR_ISOLATED
            else:
                color = COLOR_OTHER

            # Node size proportional to degree: min 18, max 42
            size = min(42, max(18, 16 + deg * 2.5))
            if selected_user and node_id == selected_user:
                size = max(size, 34)

            # Rich HTML tooltip
            tooltip = f"""
            <div style="font-family: sans-serif; padding: 6px 10px; font-size: 13px;">
                <b>{html.escape(name)}</b> (@{html.escape(username)})<br/>
                Branch: <b>{html.escape(branch)}</b> &nbsp;|&nbsp; Year {year}<br/>
                Degree: <b>{deg} friends</b><br/>
                Interests: <i>{html.escape(interests)}</i>
            </div>
            """

            net.add_node(
                node_id,
                label=name,
                title=tooltip,
                color=color,
                size=size,
                borderWidth=2,
                font={"size": 12, "color": "#1E293B", "face": "sans-serif"},
            )

        # Add edges
        adj = graph.get_adjacency_list()
        seen_edges = set()
        for u in sorted_nodes:
            for v in adj.get(u, set()):
                if v in sorted_nodes:
                    edge = (min(u, v), max(u, v))
                    if edge not in seen_edges:
                        seen_edges.add(edge)
                        is_path_edge = edge in path_edges_set
                        if is_path_edge:
                            net.add_edge(edge[0], edge[1], color=COLOR_EDGE_PATH, width=4)
                        else:
                            net.add_edge(edge[0], edge[1], color=COLOR_EDGE_NORMAL, width=1.5)

        # Generate HTML string
        html_content = net.generate_html()

        # Render iframe component inside container
        st.components.v1.html(html_content, height=600, scrolling=False)

    except Exception as exc:
        st.warning(f"Interactive PyVis view fallback to Matplotlib ({exc}).")
        fig = render_social_graph(
            graph=graph,
            user_manager=user_manager,
            selected_user=selected_user,
            recommended_users=recommended_users,
            path_nodes=path_nodes,
        )
        st.pyplot(fig)


def render_static_graph_download(
    graph: SocialGraph,
    user_manager: UserManager,
    selected_user: Optional[str] = None,
    recommended_users: Optional[List[str]] = None,
    path_nodes: Optional[List[str]] = None,
) -> None:
    """Render a Matplotlib static graph download button."""
    fig = render_social_graph(
        graph=graph,
        user_manager=user_manager,
        selected_user=selected_user,
        recommended_users=recommended_users,
        path_nodes=path_nodes,
    )
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=200, bbox_inches="tight")
    buf.seek(0)
    st.download_button(
        label="📥 Download High-Res Graph (PNG)",
        data=buf,
        file_name="campus_network_graph.png",
        mime="image/png",
        use_container_width=True,
    )
