import json
from utils.groq_client import generate
from utils.db import get_all_context_text, get_tasks, get_reports

meetings, docs = get_all_context_text()
tasks = get_tasks()
reports = get_reports()
context_blocks = []
for m in meetings: context_blocks.append(f"[Meeting: {m['title']}]\n{m['raw_text'][:2000]}")
for d in docs: context_blocks.append(f"[Document: {d['filename']}]\n{d['extracted_text'][:2000]}")
if tasks: context_blocks.append("[Tasks]\n" + "\n".join([f"- {t['title']}" for t in tasks]))
if reports: context_blocks.append("[Reports]\n" + "\n".join([f"- {r['title']}" for r in reports]))
context = "\n\n---\n\n".join(context_blocks) if context_blocks else "No stored context available."

def ask(prompt):
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
    return generate(full_prompt)

print("\nUser: Hello\nAssistant:", ask("Hello"))
print("\nUser: What is AI?\nAssistant:", ask("What is AI?"))
print("\nUser: Summarize my latest meeting\nAssistant:", ask("Summarize my latest meeting"))
