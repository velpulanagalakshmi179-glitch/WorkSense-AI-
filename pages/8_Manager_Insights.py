from utils.auth import require_login
require_login()

"""
Manager Insights: rolls up tasks + risk flags into an executive summary
for a manager audience. Deliberately reuses data already gathered by
Task Manager and Risk Center instead of re-analyzing from scratch.
"""
import streamlit as st
import pandas as pd
from utils.groq_client import generate
from utils.db import get_tasks, get_risk_flags
from utils.export_utils import export_to_pdf, export_to_txt

st.set_page_config(page_title="Manager Insights", page_icon="🧑‍💼", layout="wide")
st.title("🧑‍💼 Manager Insights")

tasks = get_tasks()
risks = get_risk_flags()

if not tasks:
    st.info("No task data yet — this page summarizes what's in Task Manager and Risk Center.")
else:
    df = pd.DataFrame(tasks)
    pending_df = df[df.status != "Completed"]

    if st.button("Generate Executive Summary", type="primary"):
        risk_text = "\n".join(f"- [{r['severity']}] {r['risk_type']}: {r['description']}" for r in risks) or "None flagged."
        prompt = f"""
Write a concise executive summary for a manager, based on this data. Structure it with
these headers exactly: "Executive Summary", "Pending Work", "Critical Risks", "Recommendations".
Keep it under 250 words total. Be specific, no generic filler.

Pending tasks:
{pending_df[['title','owner','priority','deadline']].to_csv(index=False)}

Risk flags:
{risk_text}
"""
        with st.spinner("Generating..."):
            try:
                st.session_state["manager_summary"] = generate(prompt)
            except Exception as e:
                st.error(str(e))

    summary = st.session_state.get("manager_summary")
    if summary:
        st.markdown(summary)
        st.divider()
        ec1, ec2 = st.columns(2)
        ec1.download_button("Download PDF", export_to_pdf("Manager Insights", summary),
                             file_name="manager_insights.pdf", use_container_width=True)
        ec2.download_button("Download TXT", export_to_txt("Manager Insights", summary),
                             file_name="manager_insights.txt", use_container_width=True)
