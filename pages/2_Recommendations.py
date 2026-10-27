"""Friend & Peer Recommendations Page — 2-Hop Traversal with Jaccard Interest Scoring."""

import streamlit as st
from ui.state import get_user_manager, get_social_graph, clear_bfs_state, init_session_state
from ui.styles import apply_custom_styles
from ui.components import (
    render_color_legend,
    render_student_hero,
    render_interactive_graph,
    get_avatar_initials,
)
from core.recommendation import get_friend_recommendations
from core.user_manager import display_name

init_session_state()
apply_custom_styles()

um = get_user_manager()
graph = get_social_graph()

st.title("✨ Campus Friend Recommendations")
st.caption("2-Hop Friends-of-Friends Candidate Generation & Jaccard Interest Similarity Ranking")

all_users = um.get_all_users()
if not all_users:
    st.info("No students registered yet. Add students in **Network Editor & Data**!")
    st.stop()

def u_sort_key(u):
    uid = str(u["id"])
    return (0, int(uid), uid) if uid.isdigit() else (1, 0, uid)

all_users.sort(key=u_sort_key)
user_options = {u["id"]: f"{u['name']} (@{u.get('username', u['id'])}) — {u.get('branch', 'CSE')}" for u in all_users}
user_id_list = [u["id"] for u in all_users]

# Active user selection
active_idx = 0
current_active = st.session_state.get("active_user_id")
if current_active in user_id_list:
    active_idx = user_id_list.index(current_active)

selected_uid = st.selectbox(
    "👤 Select Student to View Recommendations For:",
    options=user_id_list,
    index=active_idx,
    format_func=lambda uid: user_options.get(uid, uid),
    key="rec_student_selector",
)
st.session_state.active_user_id = selected_uid

# Render Hero profile card
render_student_hero(um, graph, selected_uid)

# Filters Row
st.subheader("🎯 Ranked Recommendations")
col_f1, col_f2, col_f3 = st.columns([1, 1, 1.5])
with col_f1:
    same_branch = st.checkbox("Same department only", value=False)
with col_f2:
    same_year = st.checkbox("Same academic year only", value=False)
with col_f3:
    all_branches = sorted(list({u.get("branch", "CSE") for u in all_users}))
    branch_pick = st.selectbox("Filter specific branch:", options=["All Branches"] + all_branches)
    selected_branch = None if branch_pick == "All Branches" else branch_pick

# Compute recommendations ONCE per run
recommendations = get_friend_recommendations(
    graph=graph,
    user_id=selected_uid,
    user_manager=um,
    same_branch_only=same_branch,
    same_year_only=same_year,
    branch_filter=selected_branch,
)

direct_friends = graph.get_friends(selected_uid)

# Empty States
if not direct_friends:
    st.info(
        f"**{display_name(um, selected_uid)}** has no direct friends yet. "
        "Recommendations require at least 1 direct friend to discover 2-hop candidates. "
        "Connect this student to someone in **Network Editor & Data**!"
    )
elif not recommendations:
    st.info(
        f"No eligible new recommendations found for **{display_name(um, selected_uid)}**. "
        "All 2-hop friends-of-friends are already direct connections, or active filters excluded candidates."
    )
else:
    st.caption(f"Found **{len(recommendations)}** candidate student(s), ordered by mutual connections and shared interests.")

    for rank, rec in enumerate(recommendations, start=1):
        cand_id = rec["user_id"]
        cand_name = rec["name"]
        cand_rec = um.get_user(cand_id)
        cand_un = cand_rec.get("username", cand_id) if cand_rec else cand_id
        cand_branch = rec["branch"]
        cand_year = rec["year"]
        mutual_count = rec["mutual_count"]
        mutual_ids = rec["mutual_friends"]
        mutual_names = [display_name(um, mid) for mid in mutual_ids]
        shared_interests = rec["shared_interests"]
        jaccard = rec["jaccard"]
        initials = get_avatar_initials(cand_name)

        # Single container per card so button is nested cleanly inside
        with st.container(border=True):
            top_col1, top_col2 = st.columns([3.5, 1.5])
            with top_col1:
                st.markdown(
                    f"""
                    <div style="display: flex; align-items: center; margin-bottom: 6px;">
                        <div class="cc-avatar" style="width: 38px; height: 38px; font-size: 14px;">{initials}</div>
                        <div>
                            <span style="font-size: 16px; font-weight: 700; color: #1E293B;">#{rank} {cand_name}</span>
                            <span style="font-size: 13px; color: #64748B;">(@{cand_un})</span>
                            <div style="margin-top: 2px;">
                                <span class="cc-badge cc-badge-branch">{cand_branch}</span>
                                <span class="cc-badge cc-badge-year">Year {cand_year}</span>
                                <span class="cc-badge cc-badge-mutual">⭐ {mutual_count} Mutual Friend{'s' if mutual_count != 1 else ''}</span>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with top_col2:
                # Add Friend button directly inside card container
                if st.button("➕ Connect Friend", key=f"add_rec_btn_{cand_id}", use_container_width=True):
                    graph.add_friendship(selected_uid, cand_id)
                    clear_bfs_state()
                    st.toast(f"Connected {display_name(um, selected_uid)} with {cand_name}!", icon="🤝")
                    st.rerun()

            # Explanation details
            st.markdown(
                f"""
                <div style="font-size: 13px; color: #475569; margin-top: 4px; padding-top: 6px; border-top: 1px solid rgba(148, 163, 184, 0.2);">
                    <strong>💡 Why recommended:</strong> <em>{rec['score_explanation']}</em> 
                    {f'<span class="cc-badge cc-badge-interest">Jaccard: {jaccard:.2f}</span>' if jaccard > 0 else ''}
                    <br/>
                    <span style="color: #64748B;">Mutual friends: {', '.join(mutual_names)}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

st.markdown("---")

# Neighborhood Subgraph View
st.subheader("🔭 2-Hop Network Neighborhood")
st.caption("Visualizing the active student, direct 1st-degree friends, and 2-hop recommended candidates.")
render_color_legend(include_path=False, include_recommended=True)

rec_uids = [r["user_id"] for r in recommendations]
# Subgraph includes: selected user + direct friends + 2-hop candidates
neighborhood_nodes = set([selected_uid]).union(direct_friends).union(rec_uids)

render_interactive_graph(
    graph=graph,
    user_manager=um,
    selected_user=selected_uid,
    recommended_users=rec_uids,
    path_nodes=None,
    focused_subgraph_nodes=neighborhood_nodes if len(neighborhood_nodes) > 1 else None,
    height="520px",
)
