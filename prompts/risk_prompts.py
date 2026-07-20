def risk_prompt(tasks_summary: str) -> str:
    return f"""
Review this task/deadline data for an enterprise team and flag risks. Return ONLY JSON:
{{
  "risks": [
    {{"risk_type": "Missing Deadline | Unassigned Task | High-Risk Work | Communication Gap",
      "description": "...", "severity": "High | Medium | Low"}}
  ]
}}

Only flag risks that are actually evidenced in the data below.

Task data:
\"\"\"
{tasks_summary}
\"\"\"
"""
