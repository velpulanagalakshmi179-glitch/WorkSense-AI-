EMAIL_SYSTEM = "You write clear, professional workplace emails. No fluff, no over-formality."

EMAIL_TYPES = {
    "Professional Email": "a professional email about the topic below",
    "Follow-up Email": "a polite follow-up email referencing the topic below, asking for status",
    "Reminder Email": "a firm but courteous reminder email about the deadline/topic below",
    "Appreciation Email": "a warm appreciation/thank-you email about the topic below",
}

def email_prompt(email_type: str, context: str, recipient: str, tone: str) -> str:
    instruction = EMAIL_TYPES.get(email_type, EMAIL_TYPES["Professional Email"])
    return f"""
Write {instruction}.
Recipient: {recipient if recipient else "the team"}
Tone: {tone}
Context / details to include:
\"\"\"
{context}
\"\"\"

Return the email with a Subject line on the first line (prefixed "Subject:"), then a blank line, then the body.
"""
