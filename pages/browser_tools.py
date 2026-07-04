import streamlit as st
import webbrowser
from modules.router import execute

def load_browser_tools_page():
    st.markdown('<p class="panel-title" style="font-size:1.5rem; color:#00D9FF; letter-spacing:2px; text-transform:uppercase;">🌐 Browser Integration Hub</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([5, 5])
    
    with col1:
        with st.container(border=True):
            st.markdown('<p class="panel-title">Quick Launcher Bookmarks</p>', unsafe_allow_html=True)
            
            b_col1, b_col2, b_col3 = st.columns(3)
            with b_col1:
                if st.button("🌐\nGoogle", use_container_width=True, key="bookmark_google"):
                    res = execute("open google")
                    st.toast(res)
            with b_col2:
                if st.button("▶️\nYouTube", use_container_width=True, key="bookmark_youtube"):
                    res = execute("open youtube")
                    st.toast(res)
            with b_col3:
                if st.button("🐙\nGitHub", use_container_width=True, key="bookmark_github"):
                    res = execute("open github")
                    st.toast(res)
                    
            st.markdown('<div style="height: 15px;"></div>', unsafe_allow_html=True)
            
            # Custom URL opener
            st.markdown('<p class="panel-title" style="font-size:0.8rem;">Launch Custom URL Target</p>', unsafe_allow_html=True)
            custom_url = st.text_input("URL Address", value="", placeholder="https://example.com", key="custom_url_input")
            if st.button("🚀 Launch Website Target", use_container_width=True, key="launch_custom_url"):
                if custom_url:
                    target_url = custom_url if custom_url.startswith(("http://", "https://")) else f"https://{custom_url}"
                    webbrowser.open(target_url)
                    st.toast(f"🌐 Opened {target_url}")
                else:
                    st.toast("⚠️ Please enter a URL address first")

    with col2:
        with st.container(border=True):
            st.markdown('<p class="panel-title">Google Search Engine Console</p>', unsafe_allow_html=True)
            
            search_query = st.text_input("Search Query", value="", placeholder="Type what you want to search...", key="search_query_input")
            if st.button("🔍 Execute Google Search", use_container_width=True, key="execute_search"):
                if search_query:
                    res = execute(f"search {search_query}")
                    st.toast(res)
                else:
                    st.toast("⚠️ Please enter a search query first")
                    
            st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
            st.markdown("""
                <div style="background:rgba(0, 217, 255, 0.02); border:1px solid rgba(0, 217, 255, 0.05); padding:12px; border-radius:8px; font-family:'Outfit', sans-serif; font-size:0.75rem; color:#64748B; line-height:1.4;">
                    <span style="color:#00D9FF; font-weight:600;">ECHO X BROWSER ENGINE:</span><br>
                    All commands execute on the host's default web browser browser session. 
                    Voice control is fully enabled. Say <i>"Search [query]"</i> or <i>"Open Google/YouTube/GitHub"</i> or <i>"Close Chrome"</i> for hands-free operations.
                </div>
            """, unsafe_allow_html=True)
            
    # Quick commands console log
    with st.container(border=True):
        st.markdown('<p class="panel-title">Browser Telemetry Logs</p>', unsafe_allow_html=True)
        st.markdown("""
            <div style="font-family:'Share Tech Mono', monospace; font-size:0.75rem; color:#10B981;">
                [STATUS] Browser Engine Subsystem Online.<br>
                [SESSION] Listening on active virtual environment ports...<br>
                [SYSTEM] Ready for desktop automation inputs.
            </div>
        """, unsafe_allow_html=True)
