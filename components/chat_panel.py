import streamlit as st
from datetime import datetime


def render_chat_panel():
    """
    Renders the central Floating Chat panel displaying recent conversation logs,
    markdown responses, and the bottom command entry input.
    Shows the last 5 messages with timestamps and a live message-count badge.
    """
    total = len(st.session_state.messages)

    # ── Message-count badge ──────────────────────────────────────────────────
    st.markdown(
        f'<div style="display:flex; justify-content:space-between; align-items:center; '
        f'margin-bottom:4px; font-family:\'Share Tech Mono\', monospace; font-size:0.68rem; color:#64748B;">'
        f'<span>💬 Conversation Log</span>'
        f'<span style="background:rgba(0,217,255,0.08); border:1px solid rgba(0,217,255,0.2); '
        f'border-radius:10px; padding:1px 8px; color:#00D9FF;">{total} messages</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    with st.container(height=180, border=True):
        # Show last 5 messages with timestamp metadata
        recent = st.session_state.messages[-5:]
        for msg in recent:
            with st.chat_message(msg["role"]):
                # Timestamp — use stored value if present, else show a placeholder
                ts = msg.get("timestamp", "")
                if ts:
                    st.markdown(
                        f'<div style="font-size:0.58rem; color:#475569; '
                        f'font-family:\'Share Tech Mono\',monospace; margin-bottom:2px;">{ts}</div>',
                        unsafe_allow_html=True,
                    )
                st.markdown(msg["content"])
                if "image" in msg and msg["image"]:
                    st.image(msg["image"], use_column_width=True)

