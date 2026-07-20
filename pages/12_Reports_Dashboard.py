from utils.auth import require_login
require_login()

import streamlit as st
import json
from utils.db import get_reports_dashboard_stats, get_reports, save_report, delete_report
from utils.groq_client import generate
from utils.export_utils import export_to_pdf

st.set_page_config(page_title="Reports Dashboard", page_icon="📊", layout="wide")
st.title("📊 Reports Dashboard")
st.caption("Enterprise insights, report generation, and management.")

# --- Dashboard Metrics ---
stats = get_reports_dashboard_stats()

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Total Meetings", stats["total_meetings"])
with c2:
    st.metric("Productivity Average", f"{stats['productivity_average']}/100")
with c3:
    st.metric("High Risk Meetings", stats["high_risk_meetings"])
with c4:
    st.metric("Pending Tasks", stats["pending_tasks"])

st.divider()

# --- Report Generation ---
st.subheader("Generate New Report")
st.write("Create a comprehensive enterprise summary based on current data.")
if st.button("Generate Enterprise Summary", type="primary"):
    with st.spinner("Analyzing metrics and generating report..."):
        prompt = f"""
Write an executive enterprise summary report. Base it on the following statistics:
- Total Meetings Processed: {stats['total_meetings']}
- Average Productivity Score: {stats['productivity_average']}/100
- Meetings flagged as High Risk: {stats['high_risk_meetings']}
- Current Pending Tasks: {stats['pending_tasks']}

Include these sections: "Executive Summary", "Productivity & Engagement", "Risk Assessment", and "Recommendations". Keep it under 400 words and make it professional.
        """
        try:
            report_content = generate(prompt)
            save_report("Enterprise Summary Report", report_content)
            st.success("Report generated and saved successfully!")
        except Exception as e:
            st.error(f"Error generating report: {e}")

st.divider()

# --- Stored Reports History ---
st.subheader("Stored Reports")
reports = get_reports()

if not reports:
    st.info("No reports have been generated yet.")
else:
    for report in reports:
        with st.expander(f"📄 {report['title']} - {report['created_at']}"):
            st.markdown(report['content'])
            
            # Action buttons
            col_download, col_delete = st.columns([2, 1])
            with col_download:
                pdf_bytes = export_to_pdf(report['title'], report['content'])
                from utils.db import log_activity
                user_email = st.session_state.user['email'] if st.session_state.get('user') else 'Unknown'
                st.download_button(
                    label="Download PDF",
                    data=pdf_bytes,
                    file_name=f"report_{report['id']}.pdf",
                    mime="application/pdf",
                    key=f"dl_{report['id']}",
                    on_click=log_activity,
                    args=(user_email, 'Report Downloaded', f"Downloaded report: {report['title']}")
                )
            with col_delete:
                if st.button("Delete Report", key=f"del_{report['id']}", type="primary"):
                    delete_report(report['id'])
                    st.rerun()
