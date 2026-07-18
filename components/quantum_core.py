import streamlit as st
from modules.theme_engine import ThemeEngine

def render_quantum_core():
    """
    Renders a holographic System Core stats panel.
    Loads dynamically based on the active operating mode.
    """
    active_mode = st.session_state.get("os_mode", "quantum")
    
    # Try custom stats HTML from theme
    stats_html = ThemeEngine.get_theme_stats_html(active_mode)
    
    # Fallback to quantum if the active theme doesn't specify one
    if stats_html is None:
        stats_html = ThemeEngine.get_theme_stats_html("quantum")
        
    # Final default hardcoded fallback
    if stats_html is None:
        stats_html = """
        <div style="font-family: monospace; color:#00D9FF; padding:10px;">
            SYSTEM CORE STATUS: ACTIVE
        </div>
        """
        
    clean_stats = "\n".join([line.strip() for line in stats_html.split("\n") if line.strip()])
    with st.container(border=True):
        st.html(clean_stats)


