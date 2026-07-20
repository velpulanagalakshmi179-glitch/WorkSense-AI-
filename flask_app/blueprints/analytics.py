from flask import Blueprint, render_template, session, redirect, url_for
from utils.db import get_tasks, get_productivity_history, get_meetings, get_risk_flags
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')

@analytics_bp.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))
        
    tasks = get_tasks()
    history = get_productivity_history()
    meetings = get_meetings()
    risk_flags = get_risk_flags()
    
    fig_prod_json = None
    fig_meet_json = None
    fig_task_json = None
    fig_risk_json = None
    
    # 1. Productivity Trend
    if history:
        hist_df = pd.DataFrame(history)
        fig_prod = px.line(
            hist_df, 
            x="week_label", 
            y=["productivity_score", "team_efficiency"],
            labels={"value": "Score", "variable": "Metric", "week_label": "Week"},
            markers=True,
            title="Score & Efficiency Over Time"
        )
        fig_prod.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        fig_prod_json = fig_prod.to_json()
        
    # 2. Meeting Volume
    if meetings:
        meet_df = pd.DataFrame(meetings)
        meet_df['date'] = pd.to_datetime(meet_df['created_at']).dt.date
        meet_counts = meet_df.groupby('date').size().reset_index(name='count')
        
        fig_meet = px.bar(
            meet_counts, 
            x='date', 
            y='count',
            labels={"date": "Date", "count": "Meetings Processed"},
            title="Meetings Processed Over Time",
            color_discrete_sequence=['#2563EB']
        )
        fig_meet_json = fig_meet.to_json()
        
    # 3. Task Completion
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
            color_discrete_map={'Completed': '#10B981', 'Pending': '#F59E0B', 'In Progress': '#3B82F6'}
        )
        fig_task.update_traces(textposition='inside', textinfo='percent+label')
        fig_task_json = fig_task.to_json()
        
    # 4. Risk Distribution
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
            color_discrete_map={'High': '#EF4444', 'Medium': '#F59E0B', 'Low': '#6B7280'}
        )
        fig_risk_json = fig_risk.to_json()

    return render_template(
        'analytics.html',
        fig_prod_json=fig_prod_json,
        fig_meet_json=fig_meet_json,
        fig_task_json=fig_task_json,
        fig_risk_json=fig_risk_json
    )
