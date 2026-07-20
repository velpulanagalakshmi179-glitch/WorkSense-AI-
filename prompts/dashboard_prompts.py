DASHBOARD_SYSTEM = (
    "You are an expert Executive Operations AI. "
    "Your goal is to analyze workplace data and provide sharp, actionable insights."
)

def executive_insights_prompt(stats, deadlines):
    return f"""
Analyze the following team statistics and upcoming deadlines to provide an executive insight report.

Team Stats:
- Meetings Processed: {stats.get('total_meetings', 0)}
- Productivity Average: {stats.get('productivity_average', 0)}/100
- High Risk Meetings: {stats.get('high_risk_meetings', 0)}
- Pending Tasks: {stats.get('pending_tasks', 0)}

Upcoming Deadlines:
{deadlines if deadlines else 'None'}

Return a JSON with the following structure:
{{
    "overall_productivity": "A brief summary of overall productivity",
    "team_performance": "A brief assessment of team performance",
    "high_priority_tasks": "Identification of critical tasks",
    "recommendations": "2-3 bullet points of actionable advice"
}}
"""

def meeting_health_prompt(recent_meetings_summary):
    return f"""
Analyze the following summaries of recent meetings to determine an overall Meeting Health Score.

Recent Meetings:
{recent_meetings_summary if recent_meetings_summary else 'No recent meetings to analyze.'}

Based on the topics discussed, action items generated, and risks flagged, provide an estimated score (0-100) for the following metrics:
- Communication Score (How clear and effective was the communication?)
- Decision Quality (Were clear decisions made?)
- Participation (Did it seem like a collaborative effort?)
- Time Efficiency (Were they productive?)
- Overall Health Score (The average or weighted total)

Return exactly in this JSON format:
{{
    "communication_score": 85,
    "decision_quality": 70,
    "participation": 80,
    "time_efficiency": 75,
    "overall_health_score": 78
}}
"""
