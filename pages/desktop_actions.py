import streamlit as st
import os
import glob
from modules.router import execute
from modules.memory import save_memory

def load_desktop_actions_page():
    st.markdown('<p class="panel-title" style="font-size:1.5rem; color:#00D9FF; letter-spacing:2px; text-transform:uppercase;">🖥️ Desktop Automation Console</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([5, 5])
    
    with col1:
        with st.container(border=True):
            st.markdown('<p class="panel-title">Application Launcher</p>', unsafe_allow_html=True)
            
            # Application buttons in 2 columns
            app_col1, app_col2 = st.columns(2)
            
            with app_col1:
                if st.button("🌐 Launch Chrome", use_container_width=True, key="launch_chrome"):
                    res = execute("open chrome")
                    st.toast(res)
                    
                if st.button("📝 Launch VS Code", use_container_width=True, key="launch_vscode"):
                    res = execute("open vs code")
                    st.toast(res)
                    
                if st.button("🧮 Launch Calculator", use_container_width=True, key="launch_calc"):
                    res = execute("open calculator")
                    st.toast(res)
                    
                if st.button("📓 Launch Notepad", use_container_width=True, key="launch_notepad"):
                    res = execute("open notepad")
                    st.toast(res)
            
            with app_col2:
                if st.button("🎨 Launch Paint", use_container_width=True, key="launch_paint"):
                    res = execute("open paint")
                    st.toast(res)
                    
                if st.button("📂 Launch Explorer", use_container_width=True, key="launch_explorer"):
                    res = execute("open explorer")
                    st.toast(res)
                    
                if st.button("🎵 Launch Spotify", use_container_width=True, key="launch_spotify"):
                    res = execute("open spotify")
                    st.toast(res)
                    
            st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
            st.markdown('<p class="panel-title" style="font-size:0.8rem;">Open User Directories</p>', unsafe_allow_html=True)
            dir_col1, dir_col2 = st.columns(2)
            with dir_col1:
                if st.button("📥 Downloads", use_container_width=True, key="open_downloads"):
                    res = execute("open downloads")
                    st.toast(res)
                if st.button("📄 Documents", use_container_width=True, key="open_docs"):
                    res = execute("open documents")
                    st.toast(res)
            with dir_col2:
                if st.button("🖥️ Desktop", use_container_width=True, key="open_desktop"):
                    res = execute("open desktop")
                    st.toast(res)
                if st.button("🖼️ Pictures", use_container_width=True, key="open_pictures"):
                    res = execute("open pictures")
                    st.toast(res)

        with st.container(border=True):
            st.markdown('<p class="panel-title">Virtual Mouse & Keyboard Input</p>', unsafe_allow_html=True)
            
            # Keyboard typing
            text_input = st.text_input("Simulate Keyboard Typing", value="", placeholder="Type text to send to active window...", key="kb_typing_input")
            if st.button("⌨️ Send Type Command", use_container_width=True, key="send_type") and text_input:
                res = execute(f"type {text_input}")
                st.toast(res)
                
            st.markdown('<div style="height: 5px;"></div>', unsafe_allow_html=True)
            
            # Mouse control
            st.markdown('<p class="panel-title" style="font-size:0.8rem;">Simulate Mouse Actions</p>', unsafe_allow_html=True)
            m_col1, m_col2, m_col3 = st.columns(3)
            with m_col1:
                if st.button("🖱️ Click", use_container_width=True, key="mouse_click"):
                    execute("click")
                    st.toast("Clicked")
            with m_col2:
                if st.button("🖱️ Double Click", use_container_width=True, key="mouse_dblclick"):
                    execute("double click")
                    st.toast("Double Clicked")
            with m_col3:
                if st.button("🖱️ Right Click", use_container_width=True, key="mouse_rtclick"):
                    execute("right click")
                    st.toast("Right Clicked")
            
            m_col4, m_col5 = st.columns(2)
            with m_col4:
                if st.button("🔼 Scroll Up", use_container_width=True, key="mouse_scrollup"):
                    execute("scroll up")
                    st.toast("Scrolled Up")
            with m_col5:
                if st.button("🔽 Scroll Down", use_container_width=True, key="mouse_scrolldown"):
                    execute("scroll down")
                    st.toast("Scrolled Down")

    with col2:
        with st.container(border=True):
            st.markdown('<p class="panel-title">System Commands & Hotkeys</p>', unsafe_allow_html=True)
            
            # Hotkey selection
            hotkey_options = {
                "Copy (Ctrl+C)": "copy",
                "Paste (Ctrl+V)": "paste",
                "Cut (Ctrl+X)": "cut",
                "Undo (Ctrl+Z)": "undo",
                "Redo (Ctrl+Y)": "redo",
                "Select All (Ctrl+A)": "select all",
                "Switch Window (Alt+Tab)": "alt tab",
                "Show Desktop (Win+D)": "show desktop",
                "Press Enter": "press enter",
                "Press Tab": "press tab",
                "Press Escape": "press escape",
                "Press Backspace": "press backspace",
                "Press Delete": "press delete",
                "Press Space": "press space"
            }
            
            selected_hotkey = st.selectbox("Virtual Hotkeys Trigger", options=list(hotkey_options.keys()))
            if st.button("⚡ Trigger Hotkey", use_container_width=True, key="trigger_hotkey"):
                cmd = hotkey_options[selected_hotkey]
                res = execute(cmd)
                st.toast(res)
                
            st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
            st.markdown('<p class="panel-title" style="font-size:0.8rem;">Power & Lock States</p>', unsafe_allow_html=True)
            p_col1, p_col2 = st.columns(2)
            with p_col1:
                if st.button("🔒 Lock PC", use_container_width=True, key="lock_pc_btn"):
                    execute("lock pc")
                if st.button("💤 Sleep PC", use_container_width=True, key="sleep_pc_btn"):
                    execute("sleep")
            with p_col2:
                # Add confirmation popups for destructive actions if needed
                if st.button("🔄 Restart", use_container_width=True, key="restart_btn", help="Triggers instant system restart"):
                    execute("restart")
                if st.button("⛔ Shutdown", use_container_width=True, key="shutdown_btn", help="Triggers instant system shutdown"):
                    execute("shutdown")

        # Screenshot Center
        with st.container(border=True):
            st.markdown('<p class="panel-title">📸 Screen Control Hub</p>', unsafe_allow_html=True)
            
            if st.button("📸 Capture System Screenshot", use_container_width=True, key="take_screenshot_action"):
                res = execute("take screenshot")
                st.toast("Screenshot Taken!")
                st.rerun()
                
            # List files in screenshots/ folder
            st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
            st.markdown('<p class="panel-title" style="font-size:0.8rem;">Recent Captures</p>', unsafe_allow_html=True)
            
            screenshot_files = sorted(glob.glob("screenshots/screenshot_*.png"), key=os.path.getmtime, reverse=True)
            
            if screenshot_files:
                latest_screenshot = screenshot_files[0]
                st.image(latest_screenshot, caption=f"Latest: {os.path.basename(latest_screenshot)}", use_column_width=True)
                
                # Download link
                with open(latest_screenshot, "rb") as file:
                    st.download_button(
                        label="💾 Download Current Image",
                        data=file,
                        file_name=os.path.basename(latest_screenshot),
                        mime="image/png",
                        use_container_width=True
                    )
            else:
                st.markdown('<div style="text-align:center; color:#64748B; font-size:0.75rem; padding: 20px;">No captures found in screenshots/ directory.</div>', unsafe_allow_html=True)
