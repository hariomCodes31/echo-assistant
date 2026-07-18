import streamlit as st
from modules.router import execute
from modules.memory import save_memory

def render_quick_tools():
    """
    Renders the 2x4 Quick Action Tools Button Panel Grid.
    Fully linked to the operational router framework.
    """
    with st.container(border=True):
        st.markdown('<p class="panel-title">Quick Tools</p>', unsafe_allow_html=True)
        col_t1, col_t2, col_t3 = st.columns(3)
        
        with col_t1:
            if st.button("📸\nScreen", use_container_width=True, key="tool_screen"):
                st.session_state.messages.append({"role": "user", "content": "take screenshot"})
                res = execute("take screenshot")
                st.session_state.messages.append({"role": "assistant", "content": res})
                save_memory(st.session_state.messages)
                st.rerun()
                
            if st.button("📝\nVS Code", use_container_width=True, key="tool_vscode"):
                st.session_state.messages.append({"role": "user", "content": "open vs code"})
                res = execute("open vs code")
                st.session_state.messages.append({"role": "assistant", "content": res})
                save_memory(st.session_state.messages)
                st.rerun()

            if st.button("📒\nNotes", use_container_width=True, key="tool_notes"):
                st.session_state.active_view = "Notes"
                st.rerun()
                
        with col_t2:
            if st.button("🌐\nChrome", use_container_width=True, key="tool_chrome"):
                st.session_state.messages.append({"role": "user", "content": "open google"})
                res = execute("open google")
                st.session_state.messages.append({"role": "assistant", "content": res})
                save_memory(st.session_state.messages)
                st.rerun()

            if st.button("🌤\nWeather", use_container_width=True, key="tool_weather"):
                st.session_state.messages.append({"role": "user", "content": "weather in delhi"})
                res = execute("weather in delhi")
                st.session_state.messages.append({"role": "assistant", "content": res})
                save_memory(st.session_state.messages)
                st.rerun()

            if st.button("🧮\nCalc", use_container_width=True, key="tool_calc"):
                st.session_state.active_view = "Calculator"
                st.rerun()
                
        with col_t3:
            if st.button("▶️\nYouTube", use_container_width=True, key="tool_youtube"):
                st.session_state.messages.append({"role": "user", "content": "open youtube"})
                res = execute("open youtube")
                st.session_state.messages.append({"role": "assistant", "content": res})
                save_memory(st.session_state.messages)
                st.rerun()

            if st.button("🗑️\nClear", use_container_width=True, key="tool_clear"):
                st.session_state.messages = []
                save_memory([])
                st.rerun()

            # Spacer to keep grid balanced
            st.markdown('<div style="height:4px;"></div>', unsafe_allow_html=True)

