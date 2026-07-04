import streamlit as st
from components.ai_core import render_ai_core
from components.quantum_core import render_quantum_core
from components.chat_panel import render_chat_panel
from modules.voice_manager import voice_manager

def load_chat_page():
    """
    Assembles the standard Chats Workspace View matching the reference design:
    Row 1: Quantum System Core stats panel (left) + Holographic Core animation (right)
    Row 2: Chat message timeline feed
    """
    # Row 1: Quantum Core + Holographic Animation side by side
    col_stats, col_orb = st.columns([4, 6])
    
    with col_stats:
        render_quantum_core()
        
    with col_orb:
        render_ai_core(voice_manager.mic_state)
    
    # Row 2: Chat messages below
    render_chat_panel()
