"""Application state manager for Streamlit session_state.

Responsible for:
- Lazy loading and caching UserManager and SocialGraph.
- Tracking active student focus, BFS queries, visualizer step state.
- Clearing stale BFS caches upon graph mutations.
- Persistence helpers for saving, resetting, and loading datasets.
"""

from pathlib import Path
from typing import Optional, Tuple
import streamlit as st

from core.graph import SocialGraph
from core.user_manager import UserManager
from utils.data_handler import DataHandler


def get_project_root() -> Path:
    """Return the absolute Path of the project root directory."""
    return Path(__file__).resolve().parent.parent


def get_default_data_path() -> Path:
    """Return the absolute Path to data/users.json."""
    return get_project_root() / "data" / "users.json"


def get_sample_small_path() -> Path:
    """Return the absolute Path to data/sample_small.json."""
    return get_project_root() / "data" / "sample_small.json"


def clear_bfs_state() -> None:
    """Clear cached BFS path and explorer results whenever graph structure changes."""
    st.session_state.bfs_path = None
    st.session_state.bfs_distance = -1
    st.session_state.bfs_start = None
    st.session_state.bfs_target = None
    st.session_state.bfs_vis_steps = None
    st.session_state.bfs_vis_idx = 0
    st.session_state.cached_recommendations = None


def init_session_state() -> None:
    """Initialize session state variables if they do not already exist."""
    if "user_manager" not in st.session_state or "social_graph" not in st.session_state:
        default_path = get_default_data_path()
        if not default_path.exists():
            # Fallback to sample_small if users.json missing
            default_path = get_sample_small_path()
        um, sg = DataHandler.load_network(str(default_path))
        st.session_state.user_manager = um
        st.session_state.social_graph = sg

    if "active_user_id" not in st.session_state:
        all_users = st.session_state.user_manager.get_all_users()
        if all_users:
            # Default to first user sorted by ID
            def ukey(u):
                uid = str(u["id"])
                return (0, int(uid), uid) if uid.isdigit() else (1, 0, uid)
            all_users.sort(key=ukey)
            st.session_state.active_user_id = all_users[0]["id"]
        else:
            st.session_state.active_user_id = None

    if "bfs_path" not in st.session_state:
        st.session_state.bfs_path = None
    if "bfs_distance" not in st.session_state:
        st.session_state.bfs_distance = -1
    if "bfs_start" not in st.session_state:
        st.session_state.bfs_start = None
    if "bfs_target" not in st.session_state:
        st.session_state.bfs_target = None
    if "bfs_vis_steps" not in st.session_state:
        st.session_state.bfs_vis_steps = None
    if "bfs_vis_idx" not in st.session_state:
        st.session_state.bfs_vis_idx = 0
    if "cached_recommendations" not in st.session_state:
        st.session_state.cached_recommendations = None


def get_user_manager() -> UserManager:
    """Retrieve the UserManager instance from session_state."""
    init_session_state()
    return st.session_state.user_manager


def get_social_graph() -> SocialGraph:
    """Retrieve the SocialGraph instance from session_state."""
    init_session_state()
    return st.session_state.social_graph


def reset_to_default_dataset() -> None:
    """Reset the session network to the default data/users.json file."""
    default_path = get_default_data_path()
    um, sg = DataHandler.load_network(str(default_path))
    st.session_state.user_manager = um
    st.session_state.social_graph = sg
    all_users = um.get_all_users()
    if all_users:
        def ukey(u):
            uid = str(u["id"])
            return (0, int(uid), uid) if uid.isdigit() else (1, 0, uid)
        all_users.sort(key=ukey)
        st.session_state.active_user_id = all_users[0]["id"]
    else:
        st.session_state.active_user_id = None
    clear_bfs_state()


def save_current_dataset() -> bool:
    """Save the current in-memory user_manager and social_graph to data/users.json."""
    um = get_user_manager()
    sg = get_social_graph()
    save_path = get_default_data_path()
    return DataHandler.save_network(um, sg, str(save_path))
