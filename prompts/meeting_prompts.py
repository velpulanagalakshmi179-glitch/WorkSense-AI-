SUMMARY_SYSTEM = (
    "You are a precise meeting-notes analyst for an enterprise workplace tool. "
    "Only use information present in the transcript given. Never invent names, "
    "dates, or numbers that are not in the text."
)

def summary_prompt(transcript: str) -> str:
    return f"""
Analyze the following meeting transcript and return ONLY a JSON object with this exact shape:

{{
  "detailed_summary": "3-6 sentence summary of what was discussed",
  "key_highlights": ["short bullet", "short bullet"],
  "decisions": ["decision made", "decision made"],
  "action_items": [
    {{"task": "...", "owner": "name or 'Unassigned'", "deadline": "date or 'Not specified'"}}
  ],
  "productivity_score": 85,
  "risks": ["risk 1", "risk 2"],
  "manager_insights": "Brief insight for managers based on the meeting tone and progress"
}}

Transcript:
\"\"\"
{transcript}
\"\"\"
"""
