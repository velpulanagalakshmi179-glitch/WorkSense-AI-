from utils.auth import require_login
require_login()

"""
Weekly Progress Report: pulls real productivity_snapshots history (saved
by Analytics) plus current task counts, and has Groq write the
narrative. This is where the Export Module's PDF/TXT download lives
front-and-center, since "report" implies "something to hand someone."
"""
import streamlit as st
import pandas as pd
from utils.groq_client import generate
from utils.db import get_tasks, get_productivity_history
from utils.export_utils import export_to_pdf, export_to_txt

st.set_page_config(page_title="Weekly Progress Report", page_icon="📈", layout="wide")
st.title("📈 Weekly Progress Report")

tasks = get_tasks()
history = get_productivity_history()

if not tasks:
    st.info("Add tasks and run Productivity Analytics at least once before generating a report.")
else:
    df = pd.DataFrame(tasks)
    completed = df[df.status == "Completed"]
    pending = df[df.status != "Completed"]

    st.subheader("This Week's Numbers")
    c1, c2, c3 = st.columns(3)
    c1.metric("Completed Tasks", len(completed))
    c2.metric("Pending Tasks", len(pending))
    c3.metric("Total Tasks", len(df))

    if history:
        st.line_chart(pd.DataFrame(history).set_index("week_label")[["productivity_score", "team_efficiency"]])

    if st.button("Generate Weekly Report", type="primary"):
        prompt = f"""
Write a weekly progress report with these sections exactly: "Team Progress",
"Completed Tasks", "Pending Tasks", "Productivity Analysis". Base it only on
the data below, be specific, under 300 words.

Completed tasks:
{completed[['title','owner']].to_csv(index=False) if len(completed) else 'None'}

Pending tasks:
{pending[['title','owner','priority','deadline']].to_csv(index=False) if len(pending) else 'None'}

Productivity history (score/efficiency over time):
{pd.DataFrame(history).to_csv(index=False) if history else 'No history yet.'}
"""
        with st.spinner("Writing report..."):
            try:
                st.session_state["weekly_report"] = generate(prompt)
            except Exception as e:
                st.error(str(e))

    report = st.session_state.get("weekly_report")
    if report:
        st.divider()
        st.markdown(report)
        ec1, ec2 = st.columns(2)
        from utils.db import log_activity
        user_email = st.session_state.user['email'] if st.session_state.get('user') else 'Unknown'
        
        ec1.download_button("Download PDF", export_to_pdf("Weekly Progress Report", report),
                             file_name="weekly_report.pdf", use_container_width=True,
                             on_click=log_activity, args=(user_email, 'Report Downloaded', 'Downloaded Weekly PDF report'))
        ec2.download_button("Download TXT", export_to_txt("Weekly Progress Report", report),
                             file_name="weekly_report.txt", use_container_width=True,
                             on_click=log_activity, args=(user_email, 'Report Downloaded', 'Downloaded Weekly TXT report'))
