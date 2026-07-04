import streamlit as st

def render_chat_panel():
    """
    Renders the central Floating Chat panel displaying recent conversation logs,
    markdown responses, and the bottom command entry input.
    """
    with st.container(height=180, border=True):
        # Scan and output recent state coordinates
        for msg in st.session_state.messages[-3:]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if "image" in msg and msg["image"]:
                    st.image(msg["image"], use_column_width=True)
