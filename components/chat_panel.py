import streamlit as st
import textwrap


def render_chat_panel():
    """
    Renders the central Chat Panel as a futuristic floating HUD monitor.
    Overhauled with double-corner brackets, glowing indicator chips, and custom heights.
    """
    total = len(st.session_state.messages)

    # ── Conversation log HUD Header ──
    header_html = f"""
        <div style="position:relative; width:100%; font-family:var(--font-mono); margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
            <div style="display:flex; align-items:center; gap:8px;">
                <span class="status-pulse-dot" style="width:6px; height:6px; background:var(--neon-cyan); border-radius:50%; display:inline-block; animation:status-pulse 1.2s infinite; box-shadow:var(--glow-cyan-xs);"></span>
                <span style="font-size:0.68rem; color:var(--text-secondary); letter-spacing:1px; text-transform:uppercase;">COMMUNICATIONS STREAM</span>
            </div>
            <div class="data-chip" style="font-size:0.6rem;">{total} PKTS RECORDED</div>
        </div>
    """
    clean_header = "\n".join([line.strip() for line in header_html.split("\n") if line.strip()])
    st.html(clean_header)


    with st.container(height=230):
        # Inject scanline filter effect specifically inside the chat container block
        st.html('<div class="holo-scan-line"></div>')


        recent = st.session_state.messages[-5:]
        for msg in recent:
            with st.chat_message(msg["role"]):
                ts = msg.get("timestamp", "")
                if ts:
                    st.markdown(
                        f'<div class="data-chip" style="font-size:0.52rem; padding:1px 5px; margin-bottom:4px; opacity:0.85;">'
                        f'TAG: {ts}</div>',
                        unsafe_allow_html=True,
                    )
                st.markdown(msg["content"])
                if "image" in msg and msg["image"]:
                    st.image(msg["image"], use_column_width=True)
