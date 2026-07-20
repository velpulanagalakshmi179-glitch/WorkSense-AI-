from utils.auth import require_login
require_login()

import streamlit as st
from utils.db import get_executive_briefs, delete_executive_brief
from utils.export_utils import export_to_pdf

st.set_page_config(page_title="Executive Briefs", page_icon="📋", layout="wide")
st.title("📋 Executive Briefs History")
st.caption("View, search, and manage your automatically generated AI Executive Briefs.")

# --- Search Bar ---
search_query = st.text_input("Search briefs by title or content", placeholder="Enter keywords...")

briefs = get_executive_briefs(search_query)

if not briefs:
    st.info("No Executive Briefs found.")
else:
    for brief in briefs:
        with st.expander(f"📋 {brief['created_at']} - {brief['title']}"):
            st.markdown(brief['content'])
            
            st.divider()
            
            # Download & Delete Actions
            col_down, col_del = st.columns([2, 1])
            with col_down:
                pdf_bytes = export_to_pdf(brief['title'], brief['content'])
                st.download_button(
                    "Download PDF", 
                    pdf_bytes, 
                    file_name=f"executive_brief_{brief['id']}.pdf", 
                    key=f"down_brief_{brief['id']}"
                )
                
            with col_del:
                if st.button("Delete Brief", key=f"del_brief_{brief['id']}", type="primary"):
                    delete_executive_brief(brief['id'])
                    st.rerun()
