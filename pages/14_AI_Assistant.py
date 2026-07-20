from utils.auth import require_login
require_login()

"""
AI Workplace Assistant: chat interface that only answers from context
pulled from previously analyzed meetings, documents, tasks, and reports in SQLite.
"""
import streamlit as st
from utils.groq_client import generate
from utils.db import get_all_context_text, get_tasks, get_reports
from utils.session_state import init_chat_history, append_chat

st.set_page_config(page_title="AI Workplace Assistant", page_icon="🤖", layout="wide")
st.title("🤖 AI Workplace Assistant")
st.caption("Ask questions across everything you've analyzed in meetings, documents, reports, and tasks.")

init_chat_history()

c1, c2 = st.columns([8, 2])
with c2:
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# --- Context Retrieval ---
meetings, docs = get_all_context_text()
tasks = get_tasks()
reports = get_reports()

if not meetings and not docs and not tasks:
    st.warning("No context yet. Add tasks or analyze a meeting/document first.")

# --- Suggested Prompts ---
st.markdown("#### Suggested Questions")
suggestions = [
    "Summarize my latest meeting.",
    "Show pending tasks.",
    "What are today's deadlines?",
    "Generate a follow-up email.",
    "Explain the uploaded document.",
    "Show my productivity score."
]

cols = st.columns(3)
selected_prompt = None
for i, s in enumerate(suggestions):
    if cols[i % 3].button(s, use_container_width=True):
        selected_prompt = s

# --- Chat Display ---
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("Ask a question...")
prompt = selected_prompt or user_input

if prompt:
    append_chat("user", prompt)
    # Only display the input if it came from the text box (buttons rerender anyway, but this is safe)
    if not selected_prompt:
        with st.chat_message("user"):
            st.write(prompt)

    context_blocks = []
    for m in meetings:
        context_blocks.append(f"[Meeting: {m['title']}]\\n{m['raw_text'][:2000]}")
    for d in docs:
        context_blocks.append(f"[Document: {d['filename']}]\\n{d['extracted_text'][:2000]}")
    if tasks:
        task_str = "\\n".join([f"- {t['title']} (Due: {t['deadline']}, Status: {t['status']}, Priority: {t['priority']})" for t in tasks])
        context_blocks.append(f"[Tasks]\\n{task_str}")
    if reports:
        report_str = "\\n".join([f"- {r['title']}: {r['content'][:500]}" for r in reports])
        context_blocks.append(f"[Reports]\\n{report_str}")
        
    context = "\\n\\n---\\n\\n".join(context_blocks) if context_blocks else "No stored context available."

    full_prompt = f"""
You are WorkSense AI, a highly capable workplace assistant. You have access to the user's local workspace context below.

Context:
\"\"\"
{context}
\"\"\"

Instructions:
1. If the user asks about their meetings, tasks, documents, or reports, use the provided context to answer. If the context does not contain the answer, say "I couldn't find any information about that in your workplace data."
2. If the user asks a general knowledge question or a greeting (e.g. "Hi", "Hello", "What is AI?"), respond naturally as a helpful AI assistant without saying that you don't have the information.
3. If the user asks "Summarize my latest meeting" and the context is empty or has no meetings, explicitly say "I couldn't find any meetings yet. Please analyze a meeting first."

Question: {prompt}
"""
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                answer = generate(full_prompt)
                st.write(answer)
                append_chat("assistant", answer)
            except Exception as e:
                st.error(str(e))
    if selected_prompt:
        st.rerun()
