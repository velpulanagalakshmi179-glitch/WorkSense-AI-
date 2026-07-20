from utils.auth import require_login
require_login()

"""
AI Risk Center: scans current task data for missing deadlines, unassigned
tasks, high-risk work, and communication gaps. Flags are persisted so
Manager Insights can pull the same data without re-calling Groq.
"""
import streamlit as st
import pandas as pd
from utils.groq_client import generate_json
from utils.db import get_tasks, add_risk_flag, get_risk_flags, clear_risk_flags
from prompts.risk_prompts import risk_prompt

st.set_page_config(page_title="AI Risk Center", page_icon="⚠️", layout="wide")
st.title("⚠️ AI Risk Center")

tasks = get_tasks()
if not tasks:
    st.info("No tasks yet — add tasks first so there's something to assess.")
else:
    df = pd.DataFrame(tasks)
    if st.button("Run Risk Scan", type="primary"):
        with st.spinner("Scanning for risks..."):
            try:
                result = generate_json(risk_prompt(df.to_csv(index=False)))
                clear_risk_flags()
                for r in result.get("risks", []):
                    add_risk_flag(r.get("risk_type", "Unknown"), r.get("description", ""), r.get("severity", "Medium"))
            except Exception as e:
                st.error(str(e))

flags = get_risk_flags()
if flags:
    severity_color = {"High": "🔴", "Medium": "🟠", "Low": "🟡"}
    for f in flags:
        icon = severity_color.get(f["severity"], "⚪")
        st.markdown(f"{icon} **{f['risk_type']}** ({f['severity']}) — {f['description']}")
else:
    st.caption("No risks flagged yet. Run a scan above.")
