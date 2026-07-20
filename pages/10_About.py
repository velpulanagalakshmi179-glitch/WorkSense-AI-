from utils.auth import require_login
require_login()

import streamlit as st

st.set_page_config(page_title="About WorkSense AI", page_icon="ℹ️", layout="wide")
st.title("ℹ️ About WorkSense AI")

st.markdown("""
**WorkSense AI** is an Enterprise SaaS-style workplace intelligence assistant built for
hackathon demonstration. It turns unstructured meeting and document content into
summaries, action items, risk flags, and reports.

### Architecture
Streamlit (UI) → Python business logic (`utils/`) → Groq API (`groq_client.py`)
→ SQLite (`worksense.db`, persistence) → ReportLab / plain text (Export Module)

### Honest scope notes
- Built on Streamlit: great for a fast demo, not a substitute for real multi-user auth
  or horizontal scaling — don't oversell it as "production" without those pieces.
- Productivity scores and risk flags are Groq's read of whatever task data currently
  exists in this session's database — they're only as good as the tasks you've entered.
- Long documents are summarized from their first chunk only; full map-reduce
  summarization for very large files is a next step, not yet implemented.

### Tech Stack
Python · Streamlit · Groq API · SQLite · Pandas · PyPDF2 · python-docx · ReportLab
""")
