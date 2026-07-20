def productivity_prompt(tasks_summary: str) -> str:
    return f"""
Given this snapshot of team tasks, estimate productivity. Return ONLY JSON:
{{
  "productivity_score": 0-100 integer,
  "team_efficiency": 0-100 integer,
  "reasoning": "1-2 sentence justification",
  "ai_suggestions": ["suggestion 1", "suggestion 2", "suggestion 3"]
}}

Note: base the score on completion rate, overdue items, and workload balance
visible in the data below — do not fabricate specifics not present in it.

Task data:
\"\"\"
{tasks_summary}
\"\"\"
"""
