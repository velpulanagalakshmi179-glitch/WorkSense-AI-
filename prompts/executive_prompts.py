EXECUTIVE_SYSTEM = (
    "You are an elite Executive AI Assistant. Your task is to generate clear, actionable, "
    "and professional Executive Briefs based on workplace statistics."
)

def executive_brief_prompt(stats, health_score, latest_meeting_title):
    return f"""
Generate an Executive Brief following the recent meeting: "{latest_meeting_title}".

Based on the following global platform statistics:
- Meetings Analyzed: {stats.get('total_meetings', 0)}
- Decisions Taken: (Estimated from recent meetings)
- Total Tasks: {stats.get('total_tasks', 0)}
- High Priority Tasks: {stats.get('high_priority_tasks', 0)}
- Pending Tasks: {stats.get('pending_tasks', 0)}
- Risks Identified: {stats.get('risks_identified', 0)}
- Overall Productivity Score: {stats.get('productivity_average', 0)}/100
- Meeting Health Score: {health_score}/100

Format the output strictly as follows (using markdown):

### Executive Summary
[Write a 2-3 sentence overview]

### Key Metrics
- **Meetings Analyzed**: {stats.get('total_meetings', 0)}
- **Total Tasks**: {stats.get('total_tasks', 0)}
- **High Priority Tasks**: {stats.get('high_priority_tasks', 0)}
- **Pending Tasks**: {stats.get('pending_tasks', 0)}
- **Risks Identified**: {stats.get('risks_identified', 0)}
- **Overall Productivity Score**: {stats.get('productivity_average', 0)}/100
- **Meeting Health Score**: {health_score}/100

### Recommended Next Actions
- [Action 1]
- [Action 2]
- [Action 3]
"""
