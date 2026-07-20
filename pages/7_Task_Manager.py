from utils.auth import require_login
require_login()

"""
Smart Task Manager: manual task CRUD + AI priority classification for
tasks that don't already have a priority set.
"""
import streamlit as st
from utils.groq_client import generate
from utils.db import get_tasks, add_task, update_task_status, delete_task

st.set_page_config(page_title="Smart Task Manager", page_icon="✅", layout="wide")
st.title("✅ Smart Task Manager")

with st.form("add_task_form", clear_on_submit=True):
    c1, c2, c3 = st.columns([3, 2, 2])
    title = c1.text_input("Task")
    owner = c2.text_input("Owner")
    deadline = c3.text_input("Deadline (optional)")
    submitted = st.form_submit_button("Add Task")
    if submitted and title.strip():
        add_task(title=title, owner=owner or None, deadline=deadline or None, source="Manual")
        st.toast("✅ Task added successfully.")
        st.rerun()

st.divider()
tasks = get_tasks()
if not tasks:
    st.caption("No tasks yet.")
else:
    for t in tasks:
        c1, c2, c3, c4, c5 = st.columns([4, 2, 2, 2, 1])
        c1.write(t["title"])
        c2.write(t["owner"] or "Unassigned")

        if t["priority"] in (None, "Medium") and c3.button("Classify", key=f"classify_{t['id']}"):
            with st.spinner("..."):
                try:
                    resp = generate(
                        f"Classify this task's priority as exactly one word - High, Medium, or Low: '{t['title']}'"
                    )
                    st.session_state[f"priority_{t['id']}"] = resp.strip().split()[0]
                except Exception as e:
                    st.error(str(e))
        priority_display = st.session_state.get(f"priority_{t['id']}", t["priority"])
        c3.write(priority_display)

        new_status = c4.selectbox(
            "status", ["Pending", "In Progress", "Completed"],
            index=["Pending", "In Progress", "Completed"].index(t["status"]) if t["status"] in ["Pending", "In Progress", "Completed"] else 0,
            key=f"status_{t['id']}", label_visibility="collapsed",
        )
        if new_status != t["status"]:
            update_task_status(t["id"], new_status)
            st.rerun()

        if c5.button("🗑️", key=f"del_{t['id']}"):
            delete_task(t["id"])
            st.rerun()
