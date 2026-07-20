DOC_SYSTEM = (
    "You are a document intelligence assistant. Answer strictly from the "
    "provided document text. If the answer is not in the document, say so "
    "explicitly rather than guessing."
)

def doc_summary_prompt(text: str) -> str:
    return f"""
Summarize the following document in 4-6 sentences, then list 3-5 key insights as bullets.
Return ONLY JSON: {{"summary": "...", "key_insights": ["...", "..."]}}

Document:
\"\"\"
{text}
\"\"\"
"""

def doc_qa_prompt(text: str, question: str) -> str:
    return f"""
Document:
\"\"\"
{text}
\"\"\"

Question: {question}

Answer using only the document above. If the document doesn't contain the answer, say
"The document does not contain this information." Keep the answer under 150 words.
"""
