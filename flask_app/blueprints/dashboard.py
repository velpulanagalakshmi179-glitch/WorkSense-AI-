from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from utils.db import (
    get_reports_dashboard_stats, get_emails_generated_count, get_stats_summary,
    get_recent_activity, get_upcoming_deadlines, get_latest_executive_brief, get_meetings
)
from utils.groq_client import generate_json
from prompts.dashboard_prompts import DASHBOARD_SYSTEM, executive_insights_prompt, meeting_health_prompt
import plotly.graph_objects as go
import json

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))
        
    stats = get_reports_dashboard_stats()
    emails_generated = get_emails_generated_count()
    summary_stats = get_stats_summary()
    activities = get_recent_activity(limit=7)
    deadlines = get_upcoming_deadlines(limit=7)
    latest_brief = get_latest_executive_brief()
    
    # Retrieve AI insights from session if they were generated
    insights = session.get('dashboard_insights')
    health = session.get('dashboard_health')
    
    health_plot_json = None
    if health:
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
            line_color='#2563EB'
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        health_plot_json = fig.to_json()

    return render_template(
        'dashboard.html',
        user=session['user'],
        stats=stats,
        emails_generated=emails_generated,
        summary_stats=summary_stats,
        activities=activities,
        deadlines=deadlines,
        latest_brief=latest_brief,
        insights=insights,
        health=health,
        health_plot_json=health_plot_json
    )

@dashboard_bp.route('/analyze', methods=['POST'])
def analyze():
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))
        
    stats = get_reports_dashboard_stats()
    deadlines = get_upcoming_deadlines(limit=7)
    recent_meetings = get_meetings()[:5]
    
    try:
        # Insights
        deadline_str = "\n".join([f"{d['title']} due {d['deadline']}" for d in deadlines])
        insights_res = generate_json(executive_insights_prompt(stats, deadline_str), system_instruction=DASHBOARD_SYSTEM)
        session['dashboard_insights'] = insights_res
        
        # Health Score
        meeting_summaries = "\n".join([f"- {m['title']}: {m['summary']}" for m in recent_meetings])
        health_res = generate_json(meeting_health_prompt(meeting_summaries), system_instruction=DASHBOARD_SYSTEM)
        session['dashboard_health'] = health_res
        flash("Executive Analysis generated successfully!", "success")
    except Exception as e:
        flash(f"Error generating analysis: {e}", "danger")
        
    return redirect(url_for('dashboard.index'))
