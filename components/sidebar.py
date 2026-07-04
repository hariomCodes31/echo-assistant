import streamlit as st

def render_sidebar():
    """
    Renders the left sidebar navigation menu, vision upload target panel, 
    and the trademark footer branding.
    """
    # Render left sidebar layout inside flexible border container
    with st.container(border=True):
        # Inject custom styles for the active view to keep navigation logic unchanged
        active_view = st.session_state.active_view
        view_indices = {
            "Chats": 1,
            "Vision": 2,
            "Voice Settings": 3,
            "Desktop Actions": 4,
            "Browser Tools": 5,
            "Music Playbacks": 6,
            "Weather Alerts": 7,
            "System Control": 8
        }
        if active_view in view_indices:
            idx = view_indices[active_view]
            st.markdown(f"""
                <style>
                    div[data-testid="column"]:nth-of-type(1) div.stButton:nth-of-type({idx}) > button {{
                        background: rgba(0, 217, 255, 0.1) !important;
                        border-color: #00D9FF !important;
                        color: #00D9FF !important;
                        box-shadow: 0 0 15px rgba(0, 217, 255, 0.2), inset 0 0 10px rgba(0, 217, 255, 0.05) !important;
                    }}
                </style>
            """, unsafe_allow_html=True)

        # OS Brand Header inside a clean, single HTML block
        st.markdown("""
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 15px;">
                <div style="width: 32px; height: 32px; border-radius: 50%; border: 3px solid #00D9FF; box-shadow: 0 0 8px #00D9FF; display: flex; justify-content: center; align-items: center;">
                    <div style="width: 10px; height: 10px; border-radius: 50%; background: #00D9FF;"></div>
                </div>
                <div>
                    <h3 style="margin: 0; font-size: 1.15rem; font-weight: 700; letter-spacing: 1px; color:#FFFFFF;">ECHO X</h3>
                    <p style="margin: 0; font-size: 0.6rem; color: #64748B; letter-spacing: 2px; text-transform: uppercase;">AI Desktop Assistant</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Navigation Links
        if st.button("💬 Chats", use_container_width=True, key="side_chats_nav"):
            st.session_state.active_view = "Chats"
            st.rerun()
            
        if st.button("🖼️ Vision", use_container_width=True, key="side_vision_nav"):
            st.session_state.active_view = "Vision"
            st.rerun()
            
        if st.button("🎙️ Voice Settings", use_container_width=True, key="side_voice_settings_btn"):
            st.session_state.active_view = "Voice Settings"
            st.rerun()
            
        if st.button("🖥️ Desktop Actions", use_container_width=True, key="side_desktop_btn"):
            st.session_state.active_view = "Desktop Actions"
            st.rerun()
            
        if st.button("🌐 Browser Tools", use_container_width=True, key="side_browser_btn"):
            st.session_state.active_view = "Browser Tools"
            st.rerun()
            
        if st.button("🎵 Music Playbacks", use_container_width=True, key="side_music_btn"):
            st.session_state.active_view = "Music Playbacks"
            st.rerun()
            
        if st.button("🌤 Weather Alerts", use_container_width=True, key="side_weather_btn"):
            st.session_state.active_view = "Weather Alerts"
            st.rerun()
            
        if st.button("⚙️ System Control", use_container_width=True, key="side_control_btn"):
            st.session_state.active_view = "System Control"
            st.rerun()
        
        # Vision Input Section Header
        st.markdown('<div style="font-size:0.75rem; color:#64748B; font-weight:600; margin-top:15px; margin-bottom:5px; text-transform:uppercase; font-family:\'Share Tech Mono\', monospace;">🖼️ Vision Input</div>', unsafe_allow_html=True)
        st.file_uploader("Upload Vision Target", type=["png", "jpg", "jpeg", "webp"], key="vision_uploader", label_visibility="collapsed")
        
        # Vision Target State and Metadata Preview
        if st.session_state.get("uploaded_image") is not None:
            st.image(st.session_state.uploaded_image, use_column_width=True)
            if st.button("🗑️ Clear Target", use_container_width=True, type="secondary", key="clear_target_sidebar"):
                st.session_state.uploaded_image = None
                st.session_state.uploaded_image_mime = None
                st.session_state.uploaded_image_name = None
                st.session_state.uploaded_image_size = None
                if "vision_uploader" in st.session_state:
                    del st.session_state.vision_uploader
                if "vision_uploader_main" in st.session_state:
                    del st.session_state.vision_uploader_main
                st.rerun()
                
        # Trademark footer
        st.markdown('<div class="branding-footer">Built by Hariom™</div>', unsafe_allow_html=True)
