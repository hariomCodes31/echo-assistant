import streamlit as st
import json
from modules.memory import save_memory

def load_settings_page():
    st.markdown('<p class="panel-title" style="font-size:1.5rem; color:#00D9FF; letter-spacing:2px; text-transform:uppercase;">⚙️ Control Settings Dashboard</p>', unsafe_allow_html=True)
    
    col_left, col_right = st.columns([5, 5])
    
    # Left Column: AI Parameters & Accent Theme
    with col_left:
        with st.container(border=True):
            st.markdown('<p class="panel-title">AI Core Configuration</p>', unsafe_allow_html=True)
            
            # Model Selection
            models = [
                "llama-3.3-70b-versatile",
                "mixtral-8x7b-32768",
                "gemma2-9b-it",
                "deepseek-r1-distill-llama-70b"
            ]
            current_model = st.session_state.get("llm_model", "llama-3.3-70b-versatile")
            if current_model not in models:
                models.insert(0, current_model)
                
            selected_model = st.selectbox(
                "Primary Inference Model",
                options=models,
                index=models.index(current_model)
            )
            st.session_state.llm_model = selected_model
            
            # Temperature
            current_temp = st.session_state.get("llm_temp", 0.7)
            selected_temp = st.slider(
                "Temperature (Creativity)",
                min_value=0.0,
                max_value=1.2,
                value=float(current_temp),
                step=0.1
            )
            st.session_state.llm_temp = selected_temp
            
            # Max Tokens
            current_tokens = st.session_state.get("llm_max_tokens", 1024)
            selected_tokens = st.slider(
                "Max Generation Tokens",
                min_value=256,
                max_value=2048,
                value=int(current_tokens),
                step=128
            )
            st.session_state.llm_max_tokens = selected_tokens

        with st.container(border=True):
            st.markdown('<p class="panel-title">OS Theme Accent Selector</p>', unsafe_allow_html=True)
            
            themes = ["Cyber Cyan", "Neon Green", "Synthwave Pink", "Amber Gold", "Crimson Red", "Grape Purple"]
            current_theme = st.session_state.get("os_theme", "Cyber Cyan")
            
            selected_theme = st.selectbox(
                "Select System Accent Color",
                options=themes,
                index=themes.index(current_theme) if current_theme in themes else 0
            )
            
            if selected_theme != current_theme:
                st.session_state.os_theme = selected_theme
                st.toast(f"🎨 Theme accent changed to {selected_theme}")
                st.rerun()

    # Right Column: Memory Management & History Control
    with col_right:
        with st.container(border=True):
            st.markdown('<p class="panel-title">Memory & Database Console</p>', unsafe_allow_html=True)
            st.markdown("""
                <div style="background:rgba(255,255,255,0.01); border:1px solid rgba(255,255,255,0.03); padding:10px; border-radius:8px; margin-bottom:15px; font-family:'Share Tech Mono', monospace; font-size:0.75rem; color:#64748B;">
                    MEMORY STATUS: <span style="color:#00D9FF;">Online</span><br>
                    DATABASE PATH: root/memory.json<br>
                    RECORDS SAVED: <span style="color:#10B981;">{records} messages</span>
                </div>
            """.format(records=len(st.session_state.get("messages", []))), unsafe_allow_html=True)
            
            # Export Memory
            chat_history = st.session_state.get("messages", [])
            chat_json_str = json.dumps(chat_history, indent=4)
            
            st.download_button(
                label="📥 Export Chat History JSON",
                data=chat_json_str,
                file_name="echo_chat_history.json",
                mime="application/json",
                use_container_width=True
            )
            
            st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
            
            # Clear Memory
            if st.button("🗑️ Purge Conversational Database", use_container_width=True, type="secondary"):
                st.session_state.messages = []
                save_memory([])
                if "uploaded_image" in st.session_state:
                    st.session_state.uploaded_image = None
                st.toast("🧹 Conversation memory successfully cleared!")
                st.rerun()
                
        with st.container(border=True):
            st.markdown('<p class="panel-title">Raw Memory Telemetry</p>', unsafe_allow_html=True)
            with st.expander("Expand Core Memory Logs"):
                st.json(st.session_state.get("messages", []))
