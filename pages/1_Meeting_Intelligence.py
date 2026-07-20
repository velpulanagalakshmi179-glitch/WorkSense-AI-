from utils.auth import require_login
require_login()

"""
Meeting Intelligence: paste/upload a transcript -> Groq extracts a
structured summary, decisions, and action items. Action items can be
pushed straight into the Task Manager's SQLite table.
"""
import streamlit as st
import json
from utils.groq_client import generate_json
from utils.db import save_meeting, add_task
from prompts.meeting_prompts import summary_prompt, SUMMARY_SYSTEM
from utils.export_utils import export_to_pdf, export_to_txt

st.set_page_config(page_title="Meeting Intelligence", page_icon="🗣️", layout="wide")
st.title("🗣️ Meeting Intelligence")
st.caption("Summarizer · Key Highlights · Decision Extraction · Action Items · Deadline Detection")

meeting_title = st.text_input("Meeting title", placeholder="e.g. Sprint 4 Planning")
transcript = st.text_area("Paste meeting transcript / notes", height=250)

col1, col2 = st.columns([1, 5])
with col1:
    analyze = st.button("Analyze Meeting", type="primary", use_container_width=True)

if analyze:
    if not transcript.strip():
        st.warning("Paste a transcript first.")
    else:
        with st.spinner("Analyzing meeting with Groq..."):
            try:
                result = generate_json(summary_prompt(transcript), system_instruction=SUMMARY_SYSTEM)
                st.session_state["last_meeting_result"] = result
                save_meeting(
                    title=meeting_title or "Untitled meeting",
                    raw_text=transcript,
                    summary=result.get("detailed_summary", ""),
                    decisions=json.dumps(result.get("decisions", [])),
                    action_items=json.dumps(result.get("action_items", [])),
                    deadlines=json.dumps([item.get("deadline") for item in result.get("action_items", []) if item.get("deadline")]),
                    productivity_score=result.get("productivity_score", 0),
                    risks=json.dumps(result.get("risks", [])),
                    manager_insights=result.get("manager_insights", "")
                )
                from utils.db import log_activity, get_executive_stats, save_executive_brief, get_meetings
                from prompts.executive_prompts import executive_brief_prompt, EXECUTIVE_SYSTEM
                from prompts.dashboard_prompts import meeting_health_prompt, DASHBOARD_SYSTEM
                from utils.groq_client import generate
                
                user_email = st.session_state.user['email'] if st.session_state.get('user') else 'Unknown'
                m_title = meeting_title or 'Untitled meeting'
                log_activity(user_email, 'Meeting Created', f"Analyzed meeting: {m_title}")
                
                # Automatically generate Executive Brief
                with st.spinner("Generating AI Executive Brief..."):
                    try:
                        stats = get_executive_stats()
                        # Calculate health score dynamically
                        recent_meetings = get_meetings()[:5]
                        meeting_summaries = "\\n".join([f"- {m['title']}: {m['summary']}" for m in recent_meetings])
                        health_res = generate_json(meeting_health_prompt(meeting_summaries), system_instruction=DASHBOARD_SYSTEM)
                        overall_health = health_res.get('overall_health_score', 0) if isinstance(health_res, dict) else 0
                        
                        brief_content = generate(executive_brief_prompt(stats, overall_health, m_title), system_instruction=EXECUTIVE_SYSTEM)
                        save_executive_brief(f"Post-Meeting Brief: {m_title}", brief_content)
                    except Exception as brief_e:
                        st.warning(f"Meeting saved, but failed to generate Executive Brief: {brief_e}")
            except Exception as e:
                st.error(str(e))

result = st.session_state.get("last_meeting_result")
if result:
    st.divider()
    st.subheader("Detailed Summary")
    st.write(result.get("detailed_summary", "—"))

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Key Highlights")
        for h in result.get("key_highlights", []):
            st.markdown(f"- {h}")
    with c2:
        st.subheader("Decisions")
        for d in result.get("decisions", []):
            st.markdown(f"- {d}")

    st.subheader("Action Items")
    action_items = result.get("action_items", [])
    if action_items:
        for i, item in enumerate(action_items):
            c1, c2, c3, c4 = st.columns([4, 2, 2, 1])
            c1.write(item.get("task", ""))
            c2.write(item.get("owner", "Unassigned"))
            c3.write(item.get("deadline", "Not specified"))
            if c4.button("Add to Tasks", key=f"add_task_{i}"):
                add_task(
                    title=item.get("task", ""),
                    owner=item.get("owner"),
                    deadline=item.get("deadline"),
                    source=f"Meeting: {meeting_title or 'Untitled'}",
                )
                st.toast("✅ Added to Task Manager.")
    else:
        st.caption("No action items detected.")

    st.divider()
    export_text = (
        f"Summary:\n{result.get('detailed_summary','')}\n\n"
        f"Decisions:\n" + "\n".join(f"- {d}" for d in result.get("decisions", [])) + "\n\n"
        f"Action Items:\n" + "\n".join(
            f"- {a.get('task')} (Owner: {a.get('owner')}, Deadline: {a.get('deadline')})"
            for a in action_items
        )
    )
    ec1, ec2 = st.columns(2)
    ec1.download_button("Download PDF", export_to_pdf(meeting_title or "Meeting Summary", export_text),
                         file_name="meeting_summary.pdf", use_container_width=True)
    ec2.download_button("Download TXT", export_to_txt(meeting_title or "Meeting Summary", export_text),
                         file_name="meeting_summary.txt", use_container_width=True)
