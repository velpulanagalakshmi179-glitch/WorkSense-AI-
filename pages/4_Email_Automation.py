from utils.auth import require_login
require_login()

"""
Email Automation: generate professional/follow-up/reminder/appreciation
emails from a short context description.
"""
import streamlit as st
from utils.groq_client import generate
from prompts.email_prompts import email_prompt, EMAIL_TYPES, EMAIL_SYSTEM

st.set_page_config(page_title="Email Automation", page_icon="✉️", layout="wide")
st.title("✉️ Email Automation")

email_type = st.selectbox("Email type", list(EMAIL_TYPES.keys()))
recipient = st.text_input("Recipient (optional)", placeholder="e.g. Priya, Engineering Team")
tone = st.selectbox("Tone", ["Neutral", "Formal", "Friendly", "Urgent"])
context = st.text_area("What is this email about?", height=150,
                        placeholder="e.g. Remind the design team the wireframes are due Friday.")

if st.button("Generate Email", type="primary"):
    if not context.strip():
        st.warning("Add some context first.")
    else:
        with st.spinner("Drafting..."):
            try:
                email_text = generate(
                    email_prompt(email_type, context, recipient, tone),
                    system_instruction=EMAIL_SYSTEM,
                )
                st.session_state["generated_email"] = email_text
                from utils.db import log_activity
                user_email = st.session_state.user['email'] if st.session_state.get('user') else 'Unknown'
                log_activity(user_email, 'Email Generated', f"Generated a {tone.lower()} {email_type} email.")
            except Exception as e:
                st.error(str(e))

if st.session_state.get("generated_email"):
    st.divider()
    st.text_area("Generated Email", st.session_state["generated_email"], height=300)
    st.download_button("Download as TXT", st.session_state["generated_email"].encode("utf-8"),
                        file_name="email_draft.txt")
