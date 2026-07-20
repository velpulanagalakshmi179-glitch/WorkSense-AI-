from utils.auth import require_login
require_login()

import streamlit as st
import json
from utils.db import get_meetings, delete_meeting
from utils.export_utils import export_to_pdf

st.set_page_config(page_title="Meeting History", page_icon="📜", layout="wide")
st.title("📜 Meeting History")
st.caption("View, search, and manage your past AI meeting analyses.")

# --- Search & Filter ---
col_search, col_date = st.columns([3, 1])
with col_search:
    search_query = st.text_input("Search meetings by title or content", placeholder="Enter keywords...")
with col_date:
    date_filter = st.date_input("Filter by date", value=None)

meetings = get_meetings(search_query, date_filter)

if not meetings:
    st.info("No meetings found in your history.")
else:
    for meeting in meetings:
        with st.expander(f"📅 {meeting['created_at']} - {meeting['title'] or 'Untitled'}"):
            # Show high level stats in columns
            score = meeting.get('productivity_score', 0)
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Productivity Score", f"{score}/100")
            
            st.subheader("Summary")
            st.write(meeting.get('summary', 'No summary available.'))
            
            # Action Items
            st.subheader("Action Items & Deadlines")
            try:
                action_items = json.loads(meeting.get('action_items', '[]'))
                if action_items:
                    for item in action_items:
                        st.markdown(f"- **{item.get('task')}** (Owner: {item.get('owner')}, Deadline: {item.get('deadline')})")
                else:
                    st.write("No action items recorded.")
            except Exception:
                st.write("Could not parse action items.")

            # Risks
            st.subheader("Risks")
            try:
                risks = json.loads(meeting.get('risks', '[]'))
                if risks:
                    for risk in risks:
                        st.markdown(f"- {risk}")
                else:
                    st.write("No risks recorded.")
            except Exception:
                st.write("Could not parse risks.")
                
            # Manager Insights
            st.subheader("Manager Insights")
            st.write(meeting.get('manager_insights', 'No insights available.'))

            # Transcript
            with st.expander("Show Original Notes / Transcript"):
                st.write(meeting.get('raw_text', 'No transcript provided.'))
                
            st.divider()
            
            # Download & Delete Actions
            col_down, col_del = st.columns([2, 1])
            with col_down:
                export_text = (
                    f"Title: {meeting['title']}\n"
                    f"Date: {meeting['created_at']}\n"
                    f"Productivity Score: {score}/100\n\n"
                    f"Summary:\n{meeting.get('summary', '')}\n\n"
                    f"Manager Insights:\n{meeting.get('manager_insights', '')}\n\n"
                )
                try:
                    export_text += "Action Items:\n" + "\n".join(
                        f"- {a.get('task')} (Owner: {a.get('owner')}, Deadline: {a.get('deadline')})"
                        for a in json.loads(meeting.get('action_items', '[]'))
                    ) + "\n\n"
                    export_text += "Risks:\n" + "\n".join(f"- {r}" for r in json.loads(meeting.get('risks', '[]')))
                except Exception:
                    pass

                pdf_bytes = export_to_pdf(meeting.get('title') or "Meeting Summary", export_text)
                st.download_button(
                    "Download PDF", 
                    pdf_bytes, 
                    file_name=f"meeting_{meeting['id']}.pdf", 
                    key=f"down_{meeting['id']}"
                )
                
            with col_del:
                if st.button("Delete Meeting", key=f"del_{meeting['id']}", type="primary"):
                    delete_meeting(meeting['id'])
                    st.rerun()
