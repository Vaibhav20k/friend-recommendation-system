"""Graph visualization module using NetworkX and Matplotlib.

Responsible for:
- Converting adjacency list to a NetworkX Graph solely for layout and rendering.
- Color coding nodes: selected user, direct friends, recommended candidates, shortest path, and others.
- Highlighting shortest path edges with distinct color and thickness.
- Returning Matplotlib figures suitable for Streamlit embedding.
"""

from typing import Any, Dict, List, Optional, Set
import matplotlib
matplotlib.use("Agg")
import matplotlib.figure
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import networkx as nx

from core.graph import SocialGraph
from core.user_manager import UserManager


def render_social_graph(
    graph: SocialGraph,
    user_manager: UserManager,
    selected_user: Optional[str] = None,
    recommended_users: Optional[List[str]] = None,
    path_nodes: Optional[List[str]] = None,
    figsize: tuple = (10, 7),
) -> matplotlib.figure.Figure:
    """Render the social network graph with color-coded nodes, edges, and legend.

    Args:
        graph: The SocialGraph instance containing users and friendships.
        user_manager: The UserManager instance for user name lookups.
        selected_user: Optional ID of the currently focused/active user.
        recommended_users: Optional list/set of user IDs recommended to the selected user.
        path_nodes: Optional list of user IDs representing a BFS shortest path.
        figsize: Dimensions of the resulting matplotlib figure (width, height).

    Returns:
        matplotlib.figure.Figure: Matplotlib figure containing the styled network graph.
    """
    G = nx.Graph()

    # Add all nodes from graph.get_all_users()
    all_users = sorted(
        graph.get_all_users(),
        key=lambda u: (0, int(u)) if str(u).isdigit() else (1, str(u)),
    )
    G.add_nodes_from(all_users)

    # Add all edges from graph.get_adjacency_list()
    adj_list = graph.get_adjacency_list()
    for u, neighbors in adj_list.items():
        for v in neighbors:
            G.add_edge(u, v)

    # Generate 2D positions using nx.spring_layout(G, seed=42, k=0.8)
    pos = nx.spring_layout(G, seed=42, k=0.8)

    # Convert collections to sets for O(1) membership checking
    rec_set = set(recommended_users) if recommended_users else set()
    path_set = set(path_nodes) if path_nodes else set()
    direct_friends = graph.get_friends(selected_user or "")

    # Define node color logic:
    # - If node == selected_user: '#FF7043' (vibrant orange/coral)
    # - If node in graph.get_friends(selected_user or ""): '#42A5F5' (sky blue)
    # - If recommended_users and node in recommended_users: '#66BB6A' (emerald green)
    # - If path_nodes and node in path_nodes and node != selected_user: '#FFA726' (amber)
    # - Else: '#CFD8DC' (subtle light gray)
    node_colors = []
    node_sizes = []
    for node in G.nodes():
        if selected_user and node == selected_user:
            node_colors.append("#FF7043")
            node_sizes.append(1100)
        elif node in direct_friends:
            node_colors.append("#42A5F5")
            node_sizes.append(800)
        elif recommended_users and node in rec_set:
            node_colors.append("#66BB6A")
            node_sizes.append(800)
        elif path_nodes and node in path_set and node != selected_user:
            node_colors.append("#FFA726")
            node_sizes.append(800)
        else:
            node_colors.append("#CFD8DC")
            node_sizes.append(800)

    # Labels: display user's name from user_manager.get_user(node)["name"] (fallback to node id)
    labels = {}
    for node in G.nodes():
        user_record = user_manager.get_user(node) if user_manager else None
        if user_record and "name" in user_record and user_record["name"]:
            labels[node] = user_record["name"]
        else:
            labels[node] = str(node)

    # Identify path edges: pairs of consecutive path nodes if path_nodes provided and has >= 2 nodes
    path_edges = set()
    if path_nodes and len(path_nodes) >= 2:
        for i in range(len(path_nodes) - 1):
            u, v = str(path_nodes[i]), str(path_nodes[i + 1])
            path_edges.add((min(u, v), max(u, v)))

    # Separate non-path and path edges
    non_path_edges = []
    highlight_path_edges = []
    for u, v in G.edges():
        normalized = (min(u, v), max(u, v))
        if normalized in path_edges:
            highlight_path_edges.append((u, v))
        else:
            non_path_edges.append((u, v))

    # Create figure and axis
    fig, ax = plt.subplots(figsize=figsize, facecolor="#FFFFFF")

    # Draw non-path edges first (color '#B0BEC5', width 1.2)
    if non_path_edges:
        nx.draw_networkx_edges(
            G,
            pos,
            edgelist=non_path_edges,
            edge_color="#B0BEC5",
            width=1.2,
            alpha=0.8,
            ax=ax,
        )

    # Draw path edges on top (color '#D32F2F', width 3.5)
    if highlight_path_edges:
        nx.draw_networkx_edges(
            G,
            pos,
            edgelist=highlight_path_edges,
            edge_color="#D32F2F",
            width=3.5,
            ax=ax,
        )

    # Draw nodes
    nx.draw_networkx_nodes(
        G,
        pos,
        nodelist=list(G.nodes()),
        node_color=node_colors,
        node_size=node_sizes,
        edgecolors="#37474F",
        linewidths=1.2,
        ax=ax,
    )

    # Draw labels
    nx.draw_networkx_labels(
        G,
        pos,
        labels=labels,
        font_size=9,
        font_family="sans-serif",
        font_weight="bold",
        font_color="#212121",
        ax=ax,
    )

    # Clean figure aesthetics: title
    title_str = "Social Network Graph"
    if selected_user:
        active_rec = user_manager.get_user(selected_user) if user_manager else None
        active_name = active_rec["name"] if active_rec else selected_user
        title_str += f" — Focus: {active_name}"
    if path_nodes and len(path_nodes) >= 2:
        path_names = [labels.get(n, n) for n in path_nodes]
        title_str += f" (Shortest Path: {' ➔ '.join(path_names)})"
    ax.set_title(title_str, fontsize=13, fontweight="bold", pad=14, color="#263238")

    # Legend explaining colors (Selected User, Direct Friend, Recommendation, Shortest Path, Other)
    legend_elements = [
        mpatches.Patch(facecolor="#FF7043", edgecolor="#37474F", label="Selected User"),
        mpatches.Patch(facecolor="#42A5F5", edgecolor="#37474F", label="Direct Friend"),
        mpatches.Patch(facecolor="#66BB6A", edgecolor="#37474F", label="Recommendation"),
        mpatches.Patch(facecolor="#FFA726", edgecolor="#37474F", label="Shortest Path"),
        mpatches.Patch(facecolor="#CFD8DC", edgecolor="#37474F", label="Other"),
    ]
    if highlight_path_edges:
        legend_elements.append(
            mlines.Line2D([0], [0], color="#D32F2F", lw=3.5, label="Path Edge")
        )

    ax.legend(
        handles=legend_elements,
        loc="upper right",
        frameon=True,
        framealpha=0.9,
        facecolor="#F8F9FA",
        edgecolor="#CFD8DC",
        fontsize=9,
    )

    # Remove axes spines/ticks
    ax.set_axis_off()

    fig.tight_layout()
    return fig
