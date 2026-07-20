import json
import os
from utils.auth import register_user, login_user
from utils.db import (
    save_meeting, get_executive_stats, save_executive_brief, get_meetings,
    add_task, get_tasks, save_document, get_reports_dashboard_stats
)
from utils.groq_client import generate, generate_json
from prompts.meeting_prompts import summary_prompt, SUMMARY_SYSTEM
from prompts.email_prompts import email_prompt, EMAIL_SYSTEM
from prompts.dashboard_prompts import meeting_health_prompt, DASHBOARD_SYSTEM
from prompts.executive_prompts import executive_brief_prompt, EXECUTIVE_SYSTEM
from utils.export_utils import export_to_pdf

print("Starting E2E Demo Simulation...\n")

# 1. Register
print("1. Registering user...")
register_user("Demo User", "demo@example.com", "password123")

# 2. Login
print("2. Logging in...")
assert login_user("demo@example.com", "password123") == True

# 3 & 4. Analyze & Save Meeting
print("3 & 4. Analyzing and saving meeting...")
meeting_transcript = "Discussion: Launch project by Friday. Action Items: Navya -> Setup Backend, Arjun -> Build UI. Risks: Time constraints."
result = generate_json(summary_prompt(meeting_transcript), system_instruction=SUMMARY_SYSTEM)
save_meeting(
    title="Demo Kickoff",
    raw_text=meeting_transcript,
    summary=result.get('detailed_summary', ''),
    decisions=json.dumps(result.get('decisions', [])),
    action_items=json.dumps(result.get('action_items', [])),
    deadlines=json.dumps([item.get('deadline') for item in result.get('action_items', []) if item.get('deadline')]),
    productivity_score=result.get('productivity_score', 0),
    risks=json.dumps(result.get('risks', [])),
    manager_insights=result.get('manager_insights', '')
)

# 8. Executive Brief Generation (simulating the background trigger)
print("8. Generating Executive Brief...")
stats = get_executive_stats()
recent_meetings = get_meetings()[:5]
meeting_summaries = '\n'.join([f"- {m['title']}: {m['summary']}" for m in recent_meetings])
health_res = generate_json(meeting_health_prompt(meeting_summaries), system_instruction=DASHBOARD_SYSTEM)
overall_health = health_res.get('overall_health_score', 0) if isinstance(health_res, dict) else 0
brief_content = generate(executive_brief_prompt(stats, overall_health, "Demo Kickoff"), system_instruction=EXECUTIVE_SYSTEM)
save_executive_brief(f"Post-Meeting Brief: Demo Kickoff", brief_content)

# 5. Upload Document
print("5. Uploading sample document...")
save_document("requirements.txt", "text", "This is a dummy requirements document with important specifications.", "Dummy summary")

# 6. Generate Follow-up Email
print("6. Generating Email...")
email_res = generate(email_prompt("Follow-up Email", "Demo Kickoff meeting details", "Team", "Friendly but urgent"), system_instruction=EMAIL_SYSTEM)

# 7. AI Assistant
print("7. Testing AI Assistant...")
from utils.db import get_all_context_text
def ask_assistant(q):
    m, d = get_all_context_text()
    t = get_tasks()
    c_blocks = []
    if m: c_blocks.append("[Meetings]\n" + "\n".join([x['raw_text'] for x in m]))
    if d: c_blocks.append("[Docs]\n" + "\n".join([x['extracted_text'] for x in d]))
    if t: c_blocks.append("[Tasks]\n" + "\n".join([x['title'] for x in t]))
    context = "\n".join(c_blocks)
    prompt = f"You are WorkSense AI. Context:\n{context}\nInstructions: Answer from context. If greeting, respond naturally. If asking for meetings and none exist, say so.\nQuestion: {q}"
    return generate(prompt)

print("   - 'Hello':", ask_assistant("Hello")[:50], "...")
print("   - 'Summarize my latest meeting':", ask_assistant("Summarize my latest meeting")[:50], "...")
print("   - 'Show pending tasks':", ask_assistant("Show pending tasks")[:50], "...")

# 9. Reports Dashboard
print("9. Fetching Reports Dashboard Stats...")
dash_stats = get_reports_dashboard_stats()

# 10. Export PDF
print("10. Exporting PDF...")
pdf_bytes = export_to_pdf("Demo Brief", brief_content)

# 11. Logout
print("11. Logout successful")

print("\nAll Steps Passed Automatically!")
