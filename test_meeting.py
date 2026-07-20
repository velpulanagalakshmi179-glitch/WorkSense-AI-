import json
from utils.groq_client import generate_json, generate
from utils.db import save_meeting, get_executive_stats, save_executive_brief, get_meetings
from prompts.meeting_prompts import summary_prompt, SUMMARY_SYSTEM
from prompts.executive_prompts import executive_brief_prompt, EXECUTIVE_SYSTEM
from prompts.dashboard_prompts import meeting_health_prompt, DASHBOARD_SYSTEM

meeting_title = 'Project Review Meeting'
transcript = """Project Review Meeting

Participants:
Manager
Developer
QA Engineer

Discussion:
- Complete login module by Wednesday.
- Finish dashboard by Thursday.
- QA testing starts Friday.
- Client demo on Monday.

Action Items:
- Rahul -> Backend
- Priya -> UI
- Arjun -> Testing

Risks:
API integration may be delayed.

Deadline:
Friday"""

print('Analyzing meeting...')
result = generate_json(summary_prompt(transcript), system_instruction=SUMMARY_SYSTEM)

print('Saving meeting to DB...')
save_meeting(
    title=meeting_title,
    raw_text=transcript,
    summary=result.get('detailed_summary', ''),
    decisions=json.dumps(result.get('decisions', [])),
    action_items=json.dumps(result.get('action_items', [])),
    deadlines=json.dumps([item.get('deadline') for item in result.get('action_items', []) if item.get('deadline')]),
    productivity_score=result.get('productivity_score', 0),
    risks=json.dumps(result.get('risks', [])),
    manager_insights=result.get('manager_insights', '')
)

from utils.db import log_activity
log_activity('System', 'Meeting Created', f'Analyzed meeting: {meeting_title}')

print('Generating Executive Brief...')
stats = get_executive_stats()
recent_meetings = get_meetings()[:5]
meeting_summaries = '\n'.join([f"- {m['title']}: {m['summary']}" for m in recent_meetings])
health_res = generate_json(meeting_health_prompt(meeting_summaries), system_instruction=DASHBOARD_SYSTEM)
overall_health = health_res.get('overall_health_score', 0) if isinstance(health_res, dict) else 0

brief_content = generate(executive_brief_prompt(stats, overall_health, meeting_title), system_instruction=EXECUTIVE_SYSTEM)
save_executive_brief(f'Post-Meeting Brief: {meeting_title}', brief_content)

print('Done!')
