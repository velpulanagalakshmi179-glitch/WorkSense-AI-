from utils.auth import require_login
require_login()

"""
Document Intelligence: upload PDF/DOCX/TXT -> summary, key insights, and
free-form Q&A grounded strictly in the uploaded document.
"""
import streamlit as st
from utils.groq_client import generate_json, generate
from utils.document_processor import extract_text, chunk_text
from utils.db import save_document
from prompts.document_prompts import doc_summary_prompt, doc_qa_prompt, DOC_SYSTEM

st.set_page_config(page_title="Document Intelligence", page_icon="📄", layout="wide")
st.title("📄 Document Intelligence")
st.caption("Upload a document to get a summary, key insights, and ask it questions.")

uploaded = st.file_uploader("Upload PDF, DOCX, or TXT", type=["pdf", "docx", "txt"])

if uploaded:
    if "doc_text" not in st.session_state or st.session_state.get("doc_name") != uploaded.name:
        with st.spinner("Extracting text..."):
            try:
                text = extract_text(uploaded)
                if not text.strip():
                    st.error("No extractable text found (the PDF may be a scanned image).")
                else:
                    st.session_state["doc_text"] = text
                    st.session_state["doc_name"] = uploaded.name
                    st.session_state.pop("doc_summary", None)
                    from utils.db import log_activity
                    user_email = st.session_state.user['email'] if st.session_state.get('user') else 'Unknown'
                    log_activity(user_email, 'PDF Uploaded', f'Uploaded document: {uploaded.name}')
            except Exception as e:
                st.error(str(e))

if st.session_state.get("doc_text"):
    text = st.session_state["doc_text"]
    st.success(f"Loaded: {st.session_state['doc_name']} ({len(text):,} characters)")

    if st.button("Summarize Document", type="primary"):
        with st.spinner("Summarizing..."):
            try:
                # Only the first chunk is summarized directly; long-doc map-reduce is a TODO.
                first_chunk = chunk_text(text)[0]
                result = generate_json(doc_summary_prompt(first_chunk), system_instruction=DOC_SYSTEM)
                st.session_state["doc_summary"] = result
                save_document(uploaded.name, uploaded.name.split(".")[-1], text, result.get("summary", ""))
            except Exception as e:
                st.error(str(e))

    if st.session_state.get("doc_summary"):
        res = st.session_state["doc_summary"]
        st.subheader("Summary")
        st.write(res.get("summary", "—"))
        st.subheader("Key Insights")
        for insight in res.get("key_insights", []):
            st.markdown(f"- {insight}")

    st.divider()
    st.subheader("Ask a Question")
    question = st.text_input("Question about this document")
    if st.button("Ask") and question.strip():
        with st.spinner("Thinking..."):
            try:
                answer = generate(doc_qa_prompt(chunk_text(text)[0], question), system_instruction=DOC_SYSTEM)
                st.markdown(f"**Answer:** {answer}")
            except Exception as e:
                st.error(str(e))
else:
    st.info("Upload a document to get started.")
