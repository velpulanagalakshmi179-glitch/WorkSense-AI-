from utils.auth import require_login
require_login()

import streamlit as st
import pandas as pd
import json
import plotly.express as px
from datetime import datetime
from utils.db import get_tasks, get_productivity_history, get_meetings, get_risk_flags

st.set_page_config(page_title="Analytics Dashboard", page_icon="📊", layout="wide")
st.title("📊 Analytics Dashboard")
st.caption("Visual insights into your team's meetings, tasks, and productivity trends.")

st.divider()

# Fetch data
tasks = get_tasks()
history = get_productivity_history()
meetings = get_meetings()
risk_flags = get_risk_flags()

# Layout in a 2x2 grid
col1, col2 = st.columns(2)

# --- 1. Productivity Trend ---
with col1:
    st.subheader("Productivity Trend")
    if history:
        hist_df = pd.DataFrame(history)
        # Create a line chart with Plotly
        fig_prod = px.line(
            hist_df, 
            x="week_label", 
            y=["productivity_score", "team_efficiency"],
            labels={"value": "Score", "variable": "Metric", "week_label": "Week"},
            markers=True,
            title="Score & Efficiency Over Time"
        )
        fig_prod.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_prod, use_container_width=True)
    else:
        st.info("No productivity history found. Generate scores to see trends.")

# --- 2. Meeting Trend ---
with col2:
    st.subheader("Meeting Volume")
    if meetings:
        meet_df = pd.DataFrame(meetings)
        # Convert created_at to date only
        meet_df['date'] = pd.to_datetime(meet_df['created_at']).dt.date
        meet_counts = meet_df.groupby('date').size().reset_index(name='count')
        
        fig_meet = px.bar(
            meet_counts, 
            x='date', 
            y='count',
            labels={"date": "Date", "count": "Meetings Processed"},
            title="Meetings Processed Over Time",
            color_discrete_sequence=['#4B0082']
        )
        st.plotly_chart(fig_meet, use_container_width=True)
    else:
        st.info("No meetings processed yet.")

st.divider()

col3, col4 = st.columns(2)

# --- 3. Task Completion ---
with col3:
    st.subheader("Task Completion")
    if tasks:
        task_df = pd.DataFrame(tasks)
        task_counts = task_df['status'].value_counts().reset_index()
        task_counts.columns = ['Status', 'Count']
        
        fig_task = px.pie(
            task_counts, 
            values='Count', 
            names='Status',
            title="Pending vs Completed Tasks",
            hole=0.4,
            color='Status',
            color_discrete_map={'Completed': '#28a745', 'Pending': '#ffc107', 'In Progress': '#17a2b8'}
        )
        fig_task.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_task, use_container_width=True)
    else:
        st.info("No tasks available to visualize.")

# --- 4. Risk Distribution ---
with col4:
    st.subheader("Risk Distribution")
    # For a robust view, we extract risk severities from risk_flags. 
    # (If we also wanted to extract from meetings JSON, we could, but risk_flags is standard).
    if risk_flags:
        risk_df = pd.DataFrame(risk_flags)
        risk_counts = risk_df['severity'].value_counts().reset_index()
        risk_counts.columns = ['Severity', 'Count']
        
        fig_risk = px.bar(
            risk_counts, 
            x='Severity', 
            y='Count',
            title="Risks Categorized by Severity",
            color='Severity',
            color_discrete_map={'High': '#dc3545', 'Medium': '#fd7e14', 'Low': '#6c757d'}
        )
        st.plotly_chart(fig_risk, use_container_width=True)
    else:
        st.info("No risks have been flagged.")
