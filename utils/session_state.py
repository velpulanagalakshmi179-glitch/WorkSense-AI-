"""
Small helpers for initializing st.session_state keys so pages don't
each reinvent the same "if key not in session_state" boilerplate.
"""
import streamlit as st


def init_state(defaults: dict):
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def init_chat_history():
    init_state({"chat_history": []})


def append_chat(role: str, content: str):
    st.session_state.chat_history.append({"role": role, "content": content})
