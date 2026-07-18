import streamlit as st
import streamlit.components.v1 as stc

STATE_MAP = {
    "Idle":       "core-idle",
    "Listening":  "core-listening",
    "Processing": "core-processing",
    "Speaking":   "core-speaking",
}

def render_ai_core(mic_state="Idle"):
    """
    Renders the AI Core dynamically based on the active Operating Mode.
    Falls back to the Quantum core if not found.
    """
    state = STATE_MAP.get(mic_state, "core-idle")

    from modules.theme_engine import ThemeEngine
    active_mode = st.session_state.get("os_mode", "quantum")

    # Try active theme AI Core
    core_html = ThemeEngine.get_theme_core_html(active_mode)

    # Fallback to quantum if active theme lacks core.html
    if core_html is None:
        core_html = ThemeEngine.get_theme_core_html("quantum")

    # Ultimate fallback if files are missing
    if core_html is None:
        core_html = f"""
        <!DOCTYPE html><html><body style="background:transparent; color:#00D9FF; display:flex; justify-content:center; align-items:center; height:100vh; font-family:sans-serif;">
        <div style="font-size:2rem; animation: pulse 2s infinite;">ECHO // {state.upper()}</div>
        <style>@keyframes pulse {{ 0%, 100% {{ opacity: 0.5; }} 50% {{ opacity: 1; }} }}</style>
        </body></html>
        """

    full_html = core_html.replace("{state}", state)
    stc.html(full_html, height=430, scrolling=False)