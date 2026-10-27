"""Network Editor, Graph Mutation & Persistence Page."""

import streamlit as st
from ui.state import (
    get_user_manager,
    get_social_graph,
    clear_bfs_state,
    reset_to_default_dataset,
    save_current_dataset,
    init_session_state,
)
from ui.styles import apply_custom_styles
from utils.data_handler import DataHandler
from core.user_manager import display_name
from data.generate_dataset import generate_campus_dataset

init_session_state()
apply_custom_styles()

um = get_user_manager()
graph = get_social_graph()

st.title("⚙️ Network Editor & Data Management")
st.caption("Add/remove students and friendships, manage file persistence, upload custom graphs, and load performance datasets.")

# Tabbed Layout for Operations
tab_edit, tab_persist, tab_bench = st.tabs(
    [
        "✏️ Edit Students & Friendships",
        "💾 File Persistence & JSON",
        "⚡ Benchmark Datasets (N = 50, 200, 1000)",
    ]
)

# -----------------------------------------------------------------------------
# TAB 1: Edit Students & Friendships
# -----------------------------------------------------------------------------
with tab_edit:
    col_e1, col_e2 = st.columns(2)

    # Sub-form 1: Add New Student
    with col_e1:
        with st.container(border=True):
            st.subheader("➕ Register New Student")
            next_id = um.get_next_user_id()

            with st.form("add_student_form", clear_on_submit=True):
                st.text_input("Auto-Generated Student ID", value=next_id, disabled=True)
                new_name = st.text_input("Full Name", placeholder="e.g. Maya Sharma").strip()
                new_un = st.text_input("Unique Handle / Username (lowercase)", placeholder="e.g. maya_sharma").strip().lower()

                branch_options = ["CSE", "ECE", "IT", "ME", "CE", "EE", "AIDS"]
                new_branch = st.selectbox("Department / Branch", options=branch_options)
                new_year = st.selectbox("Academic Year", options=[1, 2, 3, 4], index=1)

                interest_tags = [
                    "coding", "web-dev", "ai", "machine-learning", "robotics",
                    "cricket", "football", "badminton", "chess", "gaming",
                    "music", "guitar", "photography", "drama", "finance", "design"
                ]
                new_interests = st.multiselect("Student Interests (2-4 recommended)", options=interest_tags, default=["coding"])

                add_submit = st.form_submit_button("Register Student", type="primary", use_container_width=True)

                if add_submit:
                    if not new_name:
                        st.error("Student full name is required.")
                    elif not new_un:
                        st.error("Unique username handle is required.")
                    elif new_un in um.username_index:
                        st.error(f"Username handle '@{new_un}' is already registered! Please choose a different handle.")
                    else:
                        success = um.add_user(
                            user_id=next_id,
                            name=new_name,
                            username=new_un,
                            branch=new_branch,
                            year=new_year,
                            interests=new_interests,
                        )
                        if success:
                            graph.add_user(next_id)
                            clear_bfs_state()
                            st.toast(f"Registered {new_name} (@{new_un}) with ID {next_id}!", icon="🎉")
                            st.rerun()
                        else:
                            st.error("Failed to add user. Check for conflicts.")

    # Sub-form 2: Remove Student
    with col_e2:
        with st.container(border=True):
            st.subheader("🗑️ Remove Student")
            all_users = um.get_all_users()
            if all_users:
                def u_sort_key(u):
                    uid = str(u["id"])
                    return (0, int(uid), uid) if uid.isdigit() else (1, 0, uid)
                all_users.sort(key=u_sort_key)
                user_options = {u["id"]: f"{u['name']} (@{u.get('username', u['id'])}) — ID: {u['id']}" for u in all_users}
                uids = [u["id"] for u in all_users]

                del_target = st.selectbox("Select Student to Remove:", options=uids, format_func=lambda uid: user_options.get(uid, uid), key="del_student_select")
                del_btn = st.button("Delete Student", type="secondary", use_container_width=True)

                if del_btn:
                    del_name = display_name(um, del_target)
                    um.remove_user(del_target)
                    graph.remove_user(del_target)
                    clear_bfs_state()
                    st.toast(f"Removed student '{del_name}' and all associated friendship edges.", icon="🗑️")
                    st.rerun()
            else:
                st.info("No students in registry to delete.")

    st.markdown("---")

    # Friendships Management Row
    col_f1, col_f2 = st.columns(2)

    # Sub-form 3: Add Friendship
    with col_f1:
        with st.container(border=True):
            st.subheader("🤝 Form New Friendship Connection")
            all_users = um.get_all_users()
            if len(all_users) >= 2:
                all_users.sort(key=lambda u: (0, int(u["id"])) if str(u["id"]).isdigit() else (1, str(u["id"])))
                u_opts = {u["id"]: f"{u['name']} (@{u.get('username', u['id'])})" for u in all_users}
                u_ids = [u["id"] for u in all_users]

                f_u1 = st.selectbox("Student 1:", options=u_ids, index=0, format_func=lambda x: u_opts.get(x, x), key="form_f_u1")
                # Default User 2 to a DIFFERENT student!
                f_u2_default = 1 if len(u_ids) > 1 else 0
                f_u2 = st.selectbox("Student 2:", options=u_ids, index=f_u2_default, format_func=lambda x: u_opts.get(x, x), key="form_f_u2")

                connect_btn = st.button("Establish Friendship", type="primary", use_container_width=True)
                if connect_btn:
                    if f_u1 == f_u2:
                        st.error("A student cannot form a friendship with themselves.")
                    elif graph.are_friends(f_u1, f_u2):
                        st.warning(f"{display_name(um, f_u1)} and {display_name(um, f_u2)} are already connected.")
                    else:
                        graph.add_friendship(f_u1, f_u2)
                        clear_bfs_state()
                        st.toast(f"Connected {display_name(um, f_u1)} and {display_name(um, f_u2)}!", icon="🤝")
                        st.rerun()
            else:
                st.info("Need at least 2 students to form friendships.")

    # Sub-form 4: Remove Friendship
    with col_f2:
        with st.container(border=True):
            st.subheader("💔 Dissolve Existing Friendship")
            all_users = um.get_all_users()
            if len(all_users) >= 2:
                all_users.sort(key=lambda u: (0, int(u["id"])) if str(u["id"]).isdigit() else (1, str(u["id"])))
                u_opts = {u["id"]: f"{u['name']} (@{u.get('username', u['id'])})" for u in all_users}
                u_ids = [u["id"] for u in all_users]

                rem_u1 = st.selectbox("Select Student:", options=u_ids, index=0, format_func=lambda x: u_opts.get(x, x), key="rem_f_u1")
                
                # BUG FIX: ONLY list current direct friends of selected user!
                current_friends = sorted(list(graph.get_friends(rem_u1)), key=lambda x: (0, int(x)) if str(x).isdigit() else (1, str(x)))

                if current_friends:
                    rem_u2 = st.selectbox(
                        "Select Friend to Disconnect:",
                        options=current_friends,
                        format_func=lambda x: f"{display_name(um, x)} (ID: {x})",
                        key="rem_f_u2",
                    )
                    rem_btn = st.button("Dissolve Friendship", use_container_width=True)
                    if rem_btn:
                        graph.remove_friendship(rem_u1, rem_u2)
                        clear_bfs_state()
                        st.toast(f"Removed friendship between {display_name(um, rem_u1)} and {display_name(um, rem_u2)}.", icon="💔")
                        st.rerun()
                else:
                    st.info(f"{display_name(um, rem_u1)} has no active friendships to dissolve.")
            else:
                st.info("Need at least 2 students in network.")

# -----------------------------------------------------------------------------
# TAB 2: File Persistence & JSON
# -----------------------------------------------------------------------------
with tab_persist:
    st.subheader("💾 File Persistence & Data Sync")
    st.markdown(
        "Save your graph edits permanently to `data/users.json`, export JSON files for backups, "
        "or upload custom JSON network datasets with real-time schema validation."
    )

    col_p1, col_p2, col_p3 = st.columns(3)

    with col_p1:
        if st.button("💾 Save Changes to Disk (`data/users.json`)", type="primary", use_container_width=True):
            if save_current_dataset():
                st.toast("Saved current network changes to disk successfully!", icon="💾")
                st.success("File saved: `data/users.json` updated.")
            else:
                st.error("Failed to save dataset to disk. Check permissions.")

    with col_p2:
        json_export = DataHandler.export_to_json_string(um, graph)
        st.download_button(
            label="📥 Download Network JSON",
            data=json_export,
            file_name="campusconnect_network.json",
            mime="application/json",
            use_container_width=True,
        )

    with col_p3:
        if st.button("🔄 Reset to Default Dataset", use_container_width=True):
            reset_to_default_dataset()
            st.toast("Reset network back to default campus dataset!", icon="🔄")
            st.rerun()

    st.markdown("---")
    st.subheader("📤 Upload & Validate Custom Network JSON")
    uploaded_file = st.file_uploader("Upload JSON File", type=["json"], help="Must contain 'users' and 'friendships' keys.")

    if uploaded_file is not None:
        raw_text = uploaded_file.read().decode("utf-8")
        new_um, new_sg, val_errors = DataHandler.load_from_string(raw_text)

        if val_errors:
            st.error("Validation Failed! Please fix the following errors:")
            for err in val_errors:
                st.markdown(f"- ❌ {err}")
        else:
            st.success(
                f"✅ JSON Validated successfully! Contains **{new_um.get_user_count()} students** "
                f"and **{new_sg.get_friendship_count()} friendships**."
            )
            if st.button("Apply and Replace Current Network", type="primary"):
                st.session_state.user_manager = new_um
                st.session_state.social_graph = new_sg
                clear_bfs_state()
                st.toast("Loaded custom network successfully!", icon="🎉")
                st.rerun()

# -----------------------------------------------------------------------------
# TAB 3: Benchmark Datasets (N = 50, 200, 1000)
# -----------------------------------------------------------------------------
with tab_bench:
    st.subheader("⚡ Load Synthetic Campus Datasets for Performance Demonstrations")
    st.markdown(
        "Demonstrate algorithmic efficiency on large networks. Generates clustered campus structures "
        "reproducibly with dense cores, cross-branch links, and disconnected components."
    )

    col_b1, col_b2 = st.columns([2, 1])
    with col_b1:
        bench_choice = st.selectbox(
            "Select Dataset Size (N Students):",
            options=[50, 200, 1000],
            format_func=lambda n: f"Campus Network N = {n:,} Students",
        )
    with col_b2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        load_bench = st.button("⚡ Generate & Load Dataset", type="primary", use_container_width=True)

    if load_bench:
        with st.spinner(f"Generating synthetic campus graph for N = {bench_choice} students..."):
            data = generate_campus_dataset(num_students=bench_choice, seed=42)
            new_um, new_sg, errs = DataHandler.load_from_string(DataHandler.export_to_json_string(
                UserManager(), SocialGraph()
            ))
            # Populate
            new_um = UserManager()
            new_sg = SocialGraph()
            for u in data["users"]:
                new_um.add_user(
                    user_id=u["id"],
                    name=u["name"],
                    username=u["username"],
                    branch=u["branch"],
                    year=u["year"],
                    interests=u["interests"],
                )
                new_sg.add_user(u["id"])
            for pair in data["friendships"]:
                new_sg.add_friendship(pair[0], pair[1])

            st.session_state.user_manager = new_um
            st.session_state.social_graph = new_sg
            all_uids = [u["id"] for u in new_um.get_all_users()]
            st.session_state.active_user_id = all_uids[0] if all_uids else None
            clear_bfs_state()
            st.toast(f"Loaded N = {bench_choice} campus graph with {new_sg.get_friendship_count()} edges!", icon="🚀")
            st.rerun()
