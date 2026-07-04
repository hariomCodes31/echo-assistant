import streamlit as st
from tools.vision import analyze_screenshot
from modules.memory import save_memory
from modules.voice_manager import voice_manager

def load_vision_page():
    """
    Assembles the Vision Workspace View:
    Left Uploader/Preview details + Center Large Holographic Preview + Right Action controls.
    """
    col_vis_left, col_vis_center, col_vis_right = st.columns([3.5, 4.5, 2.0])
    
    with col_vis_left:
        with st.container(height=380):
            st.markdown('<p class="panel-title">Upload Target</p>', unsafe_allow_html=True)
            st.file_uploader("Browse files", type=["png", "jpg", "jpeg", "webp"], key="vision_uploader_main", label_visibility="visible")
            
            # File info
            if st.session_state.get("uploaded_image") is not None:
                name = st.session_state.get("uploaded_image_name", "vision_target.png")
                mime = st.session_state.get("uploaded_image_mime", "image/png")
                size = st.session_state.get("uploaded_image_size", 0) / 1024.0
                st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); padding:10px; border-radius:8px; font-family:'Share Tech Mono', monospace; font-size:0.75rem; color:#00D9FF; margin-top:10px;">
                        NAME: {name}<br>
                        MIME: {mime}<br>
                        SIZE: {size:.1f} KB
                    </div>
                """, unsafe_allow_html=True)
                if st.button("🗑️ Clear Active Target", use_container_width=True, type="secondary", key="clear_target_main"):
                    st.session_state.uploaded_image = None
                    st.session_state.uploaded_image_mime = None
                    st.session_state.uploaded_image_name = None
                    st.session_state.uploaded_image_size = None
                    if "vision_uploader" in st.session_state:
                        del st.session_state.vision_uploader
                    if "vision_uploader_main" in st.session_state:
                        del st.session_state.vision_uploader_main
                    st.rerun()
            else:
                st.markdown('<div style="text-align:center; color:#64748B; font-size:0.8rem; margin-top:30px;">Drop image here to start analyzing.</div>', unsafe_allow_html=True)
                
    with col_vis_center:
        with st.container(height=380):
            st.markdown('<p class="panel-title">Holographic Canvas Preview</p>', unsafe_allow_html=True)
            if st.session_state.get("uploaded_image") is not None:
                st.image(st.session_state.uploaded_image, use_column_width=True)
            else:
                st.markdown('<div style="display:flex; justify-content:center; align-items:center; height:260px; color:#64748B; font-size:0.85rem;">NO SOURCE ACTIVE</div>', unsafe_allow_html=True)

    with col_vis_right:
        with st.container(height=380):
            st.markdown('<p class="panel-title">Vision Actions</p>', unsafe_allow_html=True)
            
            # Action logic helper
            def run_vision_query(cmd_str):
                if st.session_state.get("uploaded_image") is None:
                    st.toast("⚠️ Please upload an image first!")
                    return
                st.session_state.messages.append({"role": "user", "content": cmd_str})
                with st.spinner("Analyzing target..."):
                    res = analyze_screenshot(cmd_str)
                st.session_state.vision_result = res
                st.session_state.messages.append({"role": "assistant", "content": res})
                save_memory(st.session_state.messages)
                
                # TTS
                voice_manager.update_settings(
                    volume=1.0, rate=200, voice_id=None, mode="Push To Talk", enabled=True, mic_index=None
                )
                voice_manager.tts_player.speak(res)
                st.rerun()

            if st.button("🔍 Describe", use_container_width=True, key="vis_describe_btn"):
                run_vision_query("describe image")
            if st.button("🔤 Read OCR", use_container_width=True, key="vis_ocr_btn"):
                run_vision_query("read text")
            if st.button("🏷️ Objects", use_container_width=True, key="vis_objects_btn"):
                run_vision_query("what objects are there")
            if st.button("🎨 Colors", use_container_width=True, key="vis_colors_btn"):
                run_vision_query("what color is the shirt")
            if st.button("🖥️ Analyze UI", use_container_width=True, key="vis_ui_btn"):
                run_vision_query("ui analysis")
            if st.button("🐞 Find Errors", use_container_width=True, key="vis_errors_btn"):
                run_vision_query("error")
                
    # Bottom report layout
    if st.session_state.vision_result:
        st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
        with st.container():
            st.markdown('<p class="panel-title" style="color:#00D9FF; letter-spacing:1px; margin-bottom:5px;">Analysis Report Console</p>', unsafe_allow_html=True)
            st.markdown(st.session_state.vision_result)
