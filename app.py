"""
WorkSense AI - Intelligent Workplace Operations Assistant
Entry point / Home Dashboard. Streamlit auto-builds the sidebar from the
files in pages/, prefixed with numbers to control ordering.
"""
import streamlit as st
from utils.db import init_db, get_stats_summary, update_user_password
from utils.auth import init_session, login_user, register_user, logout_user, hash_password

st.set_page_config(
    page_title="WorkSense AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()
init_session()

# --- Global style ---------------------------------------------------------
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

if not st.session_state.logged_in:
    # --- Auth Gateway -----------------------------------------------------
    st.markdown("<h1 style='text-align: center;'>Welcome to WorkSense AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Intelligent Workplace Operations Assistant</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab_login, tab_signup, tab_forgot = st.tabs(["Login", "Sign Up", "Forgot Password"])
        
        with tab_login:
            st.subheader("Login")
            with st.form("login_form"):
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Log In", use_container_width=True)
                if submit:
                    if login_user(email, password):
                        st.success("Logged in successfully!")
                        st.rerun()
                    else:
                        st.error("Invalid email or password.")
        
        with tab_signup:
            st.subheader("Sign Up")
            with st.form("signup_form"):
                new_name = st.text_input("Full Name")
                new_email = st.text_input("Email")
                new_password = st.text_input("Password", type="password")
                new_org = st.text_input("Organization (Optional)")
                new_role = st.text_input("Role (Optional)")
                signup_submit = st.form_submit_button("Sign Up", use_container_width=True)
                if signup_submit:
                    if new_name and new_email and new_password:
                        if register_user(new_name, new_email, new_password, new_org, new_role):
                            st.success("Account created successfully! Please log in.")
                        else:
                            st.error("Email already registered.")
                    else:
                        st.error("Please fill out name, email, and password.")
                        
        with tab_forgot:
            st.subheader("Forgot Password")
            with st.form("forgot_form"):
                reset_email = st.text_input("Email")
                new_password_reset = st.text_input("New Password", type="password")
                reset_submit = st.form_submit_button("Reset Password", use_container_width=True)
                if reset_submit:
                    if reset_email and new_password_reset:
                        # In a real app we'd verify email, but for demo we just reset
                        update_user_password(reset_email, hash_password(new_password_reset))
                        st.success("Password updated successfully. Please log in.")
                    else:
                        st.error("Please provide your email and new password.")

else:
    # --- Executive Dashboard (Logged In) ----------------------------------
    
    # Header
    col_header, col_logout = st.columns([8, 1])
    with col_header:
        st.markdown(f"## 🧠 Executive Dashboard - Welcome {st.session_state.user['name']}!")
        st.markdown("#### High-level overview of team operations, risks, and productivity.")
    with col_logout:
        if st.button("Logout"):
            logout_user()
            st.rerun()

    st.divider()

    # --- KPI Cards ---
    from utils.db import get_reports_dashboard_stats, get_emails_generated_count, get_upcoming_deadlines, get_meetings, get_recent_activity
    import json
    import pandas as pd
    import plotly.graph_objects as go
    from utils.groq_client import generate_json
    from prompts.dashboard_prompts import DASHBOARD_SYSTEM, executive_insights_prompt, meeting_health_prompt

    stats = get_reports_dashboard_stats()
    emails_generated = get_emails_generated_count()
    
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Meetings Processed", stats["total_meetings"])
    c2.metric("Documents Uploaded", get_stats_summary()["documents_processed"])
    c3.metric("Emails Generated", emails_generated)
    c4.metric("Productivity Score", f"{stats['productivity_average']}/100")
    c5.metric("High Risk Meetings", stats["high_risk_meetings"])
    c6.metric("Pending Tasks", stats["pending_tasks"])

    st.divider()

    # --- Row 1: Activity & Deadlines ---
    row1_c1, row1_c2 = st.columns(2)
    
    with row1_c1:
        st.markdown("### 🕒 Recent Activity Timeline")
        activities = get_recent_activity(limit=7)
        if not activities:
            st.info("No recent activity found.")
        else:
            for act in activities:
                icon = "⚪"
                if act['action_type'] == "Login Time": icon = "🔑"
                elif act['action_type'] == "Meeting Created": icon = "📅"
                elif act['action_type'] == "PDF Uploaded": icon = "📄"
                elif act['action_type'] == "Email Generated": icon = "✉️"
                elif act['action_type'] == "Report Downloaded": icon = "📥"
                st.markdown(f"{icon} **{act['action_type']}** - {act['description']} _({act['created_at']})_")

    with row1_c2:
        st.markdown("### ⏰ Upcoming Deadlines")
        deadlines = get_upcoming_deadlines(limit=7)
        if not deadlines:
            st.info("No upcoming deadlines. Great job!")
        else:
            for d in deadlines:
                st.markdown(f"**{d['title']}** (Owner: {d['owner']}) - Due: **{d['deadline']}** - Priority: {d['priority']}")

    st.divider()

    # --- Executive Brief ---
    st.markdown("### 📋 Latest Executive Brief")
    from utils.db import get_latest_executive_brief
    from utils.export_utils import export_to_pdf
    
    latest_brief = get_latest_executive_brief()
    if latest_brief:
        with st.container(border=True):
            st.markdown(f"#### {latest_brief['title']}")
            st.caption(f"Generated: {latest_brief['created_at']}")
            st.markdown(latest_brief['content'])
            
            pdf_bytes = export_to_pdf(latest_brief['title'], latest_brief['content'])
            st.download_button(
                "Download Executive Brief",
                data=pdf_bytes,
                file_name="executive_brief.pdf",
                mime="application/pdf",
                key="dl_latest_brief"
            )
    else:
        st.info("No Executive Briefs generated yet. Analyze a meeting to create one automatically.")

    st.divider()

    # --- Row 2: AI Manager Insights & Health Score ---
    st.markdown("### 🤖 AI Executive Analysis")
    
    if st.button("Generate Executive Analysis", type="primary"):
        with st.spinner("Analyzing operations..."):
            try:
                # Insights
                deadline_str = "\\n".join([f"{d['title']} due {d['deadline']}" for d in deadlines])
                insights_res = generate_json(executive_insights_prompt(stats, deadline_str), system_instruction=DASHBOARD_SYSTEM)
                st.session_state['dashboard_insights'] = insights_res
                
                # Health Score
                recent_meetings = get_meetings()[:5]
                meeting_summaries = "\\n".join([f"- {m['title']}: {m['summary']}" for m in recent_meetings])
                health_res = generate_json(meeting_health_prompt(meeting_summaries), system_instruction=DASHBOARD_SYSTEM)
                st.session_state['dashboard_health'] = health_res
                
            except Exception as e:
                st.error(f"Error generating analysis: {e}")

    row2_c1, row2_c2 = st.columns(2)

    with row2_c1:
        st.markdown("#### Manager Insights")
        insights = st.session_state.get('dashboard_insights')
        if insights:
            st.markdown(f"**Overall Productivity**: {insights.get('overall_productivity')}")
            st.markdown(f"**Team Performance**: {insights.get('team_performance')}")
            st.markdown(f"**High Priority Tasks**: {insights.get('high_priority_tasks')}")
            st.markdown(f"**Recommendations**: {insights.get('recommendations')}")
        else:
            st.info("Click 'Generate Executive Analysis' to compute AI insights.")

    with row2_c2:
        st.markdown("#### Meeting Health Score")
        health = st.session_state.get('dashboard_health')
        if health:
            st.markdown(f"##### Overall Health Score: {health.get('overall_health_score', 0)}/100")
            categories = ['Communication', 'Decision Quality', 'Participation', 'Time Efficiency']
            values = [
                health.get('communication_score', 0),
                health.get('decision_quality', 0),
                health.get('participation', 0),
                health.get('time_efficiency', 0)
            ]
            
            fig = go.Figure(data=go.Scatterpolar(
              r=values + [values[0]],
              theta=categories + [categories[0]],
              fill='toself',
              line_color='#4B0082'
            ))
            fig.update_layout(
              polar=dict(
                radialaxis=dict(visible=True, range=[0, 100])
              ),
              showlegend=False,
              margin=dict(l=20, r=20, t=20, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Click 'Generate Executive Analysis' to plot Meeting Health.")

    st.divider()
    st.info("Use the sidebar to explore detailed modules like Meeting Intelligence, Document Intelligence, or Reports Dashboard.")
