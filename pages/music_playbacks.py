import streamlit as st
from modules.router import execute

def load_music_playbacks_page():
    st.markdown('<p class="panel-title" style="font-size:1.5rem; color:#00D9FF; letter-spacing:2px; text-transform:uppercase;">🎵 Music Telemetry Control</p>', unsafe_allow_html=True)
    
    # Track playing history in session state
    if "music_history" not in st.session_state:
        st.session_state.music_history = []
        
    col1, col2 = st.columns([5, 5])
    
    with col1:
        with st.container(border=True):
            st.markdown('<p class="panel-title">YouTube Music Search</p>', unsafe_allow_html=True)
            
            song_query = st.text_input("Enter Song / Artist Name", value="", placeholder="e.g. Lofi Girl, Starboy, Interstellar Theme...", key="song_query_input")
            if st.button("▶️ Search and Play Song", use_container_width=True, key="search_play_song"):
                if song_query:
                    res = execute(f"play {song_query}")
                    st.toast(res)
                    # Add to history
                    if song_query not in st.session_state.music_history:
                        st.session_state.music_history.insert(0, song_query)
                else:
                    st.toast("⚠️ Please enter a song name first")
                    
            st.markdown('<div style="height: 15px;"></div>', unsafe_allow_html=True)
            st.markdown('<p class="panel-title" style="font-size:0.8rem;">Quick Ambient Presets</p>', unsafe_allow_html=True)
            
            presets = {
                "☕ Lofi Hip Hop Beats": "lofi hip hop radio",
                "🌌 Synthwave Retro": "synthwave radio beats",
                "📚 Ambient Study Music": "ambient focus study music",
                "❄️ Chillhop Mix": "chillhop music",
                "🎹 Classical Piano": "classical piano study playlist"
            }
            
            for label, query in presets.items():
                if st.button(label, use_container_width=True, key=f"preset_{query.replace(' ', '_')}"):
                    res = execute(f"play {query}")
                    st.toast(res)
                    if label not in st.session_state.music_history:
                        st.session_state.music_history.insert(0, label)

    with col2:
        with st.container(border=True):
            st.markdown('<p class="panel-title">Spotify Integration Hub</p>', unsafe_allow_html=True)
            st.markdown("""
                <div style="background:rgba(30, 215, 96, 0.03); border:1px solid rgba(30, 215, 96, 0.1); padding:12px; border-radius:8px; margin-bottom:15px;">
                    <span style="color:#1DB954; font-weight:600; font-family:'Share Tech Mono', monospace;">SPOTIFY CONNECT</span><br>
                    <span style="font-size:0.75rem; color:#64748B;">Launch and terminate the Spotify desktop client directly. Support voice playbacks.</span>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("🟢 Launch Spotify Client", use_container_width=True, key="spotify_launch_btn"):
                res = execute("open spotify")
                st.toast(res)
                
            if st.button("🔴 Terminate Spotify Client", use_container_width=True, key="spotify_close_btn"):
                # We can kill spotify.exe
                from tools.desktop import _kill
                if _kill("Spotify.exe"):
                    st.toast("✅ Closed Spotify")
                else:
                    st.toast("⚠️ Spotify is not running")
                    
            st.markdown('<div style="height: 15px;"></div>', unsafe_allow_html=True)
            st.markdown('<p class="panel-title" style="font-size:0.8rem;">Media Player Telemetry</p>', unsafe_allow_html=True)
            st.markdown("""
                <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); padding:12px; border-radius:8px; font-family:'Share Tech Mono', monospace; font-size:0.75rem; color:#00D9FF;">
                    ACTIVE DRIVER: Chrome Browser / Spotify Client<br>
                    AUDIO CHANNEL: Windows Default Output Device<br>
                    CONTROL CODE: system_media_control (Online)
                </div>
            """, unsafe_allow_html=True)

    # Played History Timeline
    with st.container(border=True):
        st.markdown('<p class="panel-title">Session Playback History</p>', unsafe_allow_html=True)
        if st.session_state.music_history:
            for item in st.session_state.music_history[:5]:
                st.markdown(f'<div style="font-family:\'Share Tech Mono\', monospace; font-size:0.8rem; color:#64748B; padding: 4px 8px; border-bottom: 1px solid rgba(255,255,255,0.02);">🎵 {item}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="text-align:center; color:#64748B; font-size:0.75rem; padding: 10px;">No music played in this session.</div>', unsafe_allow_html=True)
