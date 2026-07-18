import streamlit as st
from modules.router import execute
from modules.memory import save_memory

def render_quick_tools():
    """
    Renders the 2x4 Quick Action Tools Button Panel Grid.
    Fully linked to the operational router framework.
    """
    with st.container(border=True):
        st.markdown('<p class="panel-title">Quick Actions</p>', unsafe_allow_html=True)
        
        # Inject custom styling for holographic button grid
        st.markdown("""
            <style>
                /* Style only the quick action buttons in the right column */
                div[data-testid="column"]:nth-of-type(3) div.stButton > button {
                    height: 68px !important;
                    background: rgba(0, 217, 255, 0.02) !important;
                    border: 1px solid rgba(0, 217, 255, 0.15) !important;
                    border-radius: var(--radius-lg) !important;
                    font-family: var(--font-mono) !important;
                    font-size: 0.65rem !important;
                    letter-spacing: 0.8px !important;
                    text-transform: uppercase !important;
                    display: flex !important;
                    flex-direction: column !important;
                    align-items: center !important;
                    justify-content: center !important;
                    gap: 6px !important;
                    line-height: 1.1 !important;
                    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
                    box-shadow: inset 0 0 10px rgba(0, 217, 255, 0.01) !important;
                }
                div[data-testid="column"]:nth-of-type(3) div.stButton > button:hover {
                    background: rgba(0, 217, 255, 0.08) !important;
                    border-color: var(--neon-cyan) !important;
                    color: var(--neon-cyan) !important;
                    box-shadow: var(--glow-cyan-xs), inset 0 0 15px rgba(0, 217, 255, 0.05) !important;
                    transform: perspective(300px) translateZ(8px) translateY(-3px) !important;
                }
            </style>
        """, unsafe_allow_html=True)

        col_t1, col_t2, col_t3 = st.columns(3)
        
        with col_t1:
            if st.button("📸\nSCREEN", use_container_width=True, key="tool_screen"):
                st.session_state.messages.append({"role": "user", "content": "take screenshot"})
                res = execute("take screenshot")
                st.session_state.messages.append({"role": "assistant", "content": res})
                save_memory(st.session_state.messages)
                st.rerun()
                
            if st.button("📝\nVS CODE", use_container_width=True, key="tool_vscode"):
                st.session_state.messages.append({"role": "user", "content": "open vs code"})
                res = execute("open vs code")
                st.session_state.messages.append({"role": "assistant", "content": res})
                save_memory(st.session_state.messages)
                st.rerun()

            if st.button("📒\nNOTES", use_container_width=True, key="tool_notes"):
                st.session_state.active_view = "Notes"
                st.rerun()
                
        with col_t2:
            if st.button("🌐\nCHROME", use_container_width=True, key="tool_chrome"):
                st.session_state.messages.append({"role": "user", "content": "open google"})
                res = execute("open google")
                st.session_state.messages.append({"role": "assistant", "content": res})
                save_memory(st.session_state.messages)
                st.rerun()

            if st.button("🌤\nWEATHER", use_container_width=True, key="tool_weather"):
                st.session_state.messages.append({"role": "user", "content": "weather in delhi"})
                res = execute("weather in delhi")
                st.session_state.messages.append({"role": "assistant", "content": res})
                save_memory(st.session_state.messages)
                st.rerun()

            if st.button("🧮\nCALC", use_container_width=True, key="tool_calc"):
                st.session_state.active_view = "Calculator"
                st.rerun()
                
        with col_t3:
            if st.button("▶️\nYOUTUBE", use_container_width=True, key="tool_youtube"):
                st.session_state.messages.append({"role": "user", "content": "open youtube"})
                res = execute("open youtube")
                st.session_state.messages.append({"role": "assistant", "content": res})
                save_memory(st.session_state.messages)
                st.rerun()

            if st.button("🗑️\nCLEAR", use_container_width=True, key="tool_clear"):
                st.session_state.messages = []
                save_memory([])
                st.rerun()

            # Spacer to keep grid balanced
            st.markdown('<div style="height:4px;"></div>', unsafe_allow_html=True)

