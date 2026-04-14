"""Standalone Streamlit app for Arsenic Awareness Chatbot."""
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.chatbot import ArsenicChatbot
from core.config.settings import settings

st.set_page_config(page_title="Arsenic Awareness Chatbot", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .stChatMessage { padding: 1rem; }
    .disclaimer { font-size: 0.85rem; color: #666; margin-top: 1rem; }
</style>
""", unsafe_allow_html=True)

if "chatbot" not in st.session_state:
    st.session_state.chatbot = ArsenicChatbot()
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.title("Arsenic Awareness")
    st.markdown("### Emergency Contacts")
    st.info("Health Helpline (Bangladesh): 16263")
    st.info("National Poison Control: 1-800-222-1222")
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.session_state.chatbot.memory.clear("streamlit")
        st.rerun()

# Main chat
st.title("Arsenic Poisoning Awareness & Skin Detection Guidance")
st.caption("Ask questions in English or Bangla. This is for awareness only - consult a doctor for medical advice.")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask about arsenic symptoms, prevention, or treatment..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = st.session_state.chatbot.chat(prompt, session_id="streamlit")
        st.markdown(result["response"])
        if result.get("sources"):
            with st.expander("Sources"):
                for s in result["sources"]:
                    st.write(f"- {s.get('source', '')} ({s.get('category', '')})")
    st.session_state.messages.append({
        "role": "assistant",
        "content": result["response"],
    })
    st.rerun()
