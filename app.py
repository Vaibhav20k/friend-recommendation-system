"""CampusConnect — Who's in Your Network?

Main application entry point orchestrating multipage navigation, global page configuration,
and shared theme session state.
"""

import streamlit as st
from ui.state import init_session_state
from ui.styles import apply_custom_styles

# 1. Page Configuration
st.set_page_config(
    page_title="CampusConnect — Social Network Explorer",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. State & CSS initialization
init_session_state()
apply_custom_styles()

# 3. Multipage Navigation Specification
pages = [
    st.Page("pages/1_Dashboard.py", title="Campus Dashboard", icon="📊", default=True),
    st.Page("pages/2_Recommendations.py", title="Friend Recommendations", icon="✨"),
    st.Page("pages/3_Path_Finder.py", title="Connection Path Finder", icon="🔍"),
    st.Page("pages/4_BFS_Visualizer.py", title="BFS Step Visualizer", icon="🚶"),
    st.Page("pages/5_Hash_Lab.py", title="Hash Table Lab", icon="🧪"),
    st.Page("pages/6_Network_Editor.py", title="Network Editor & Data", icon="⚙️"),
    st.Page("pages/7_Theory_and_Viva.py", title="Theory & Viva Guide", icon="📖"),
]

pg = st.navigation(pages)
pg.run()
