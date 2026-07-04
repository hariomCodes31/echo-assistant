import streamlit as st

def render_quantum_core():
    """
    Renders the custom holographic Quantum System Core stats panel,
    exactly matching the visual composition and styling of the reference blueprint.
    """
    with st.container(border=True):
        st.markdown('<p class="panel-title">Quantum System Core</p>', unsafe_allow_html=True)
        
        # Neural Link
        st.markdown("""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; font-family:'Outfit', sans-serif; font-size:0.8rem;">
                <div style="display:flex; align-items:center; gap:8px; color:#64748B;">
                    <span style="color:#10B981; font-size:0.75rem;">🟢</span> Neural Link
                </div>
                <div style="color:#10B981; font-weight:600; font-family:'Share Tech Mono', monospace; text-shadow: 0 0 8px rgba(16,185,129,0.3);">CONNECTED</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Memory Bank
        st.markdown("""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; font-family:'Outfit', sans-serif; font-size:0.8rem;">
                <div style="display:flex; align-items:center; gap:8px; color:#64748B;">
                    <span style="color:#10B981; font-size:0.75rem;">💾</span> Memory Bank
                </div>
                <div style="color:#10B981; font-weight:600; font-family:'Share Tech Mono', monospace; text-shadow: 0 0 8px rgba(16,185,129,0.3);">ACTIVE</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Learning Engine
        st.markdown("""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; font-family:'Outfit', sans-serif; font-size:0.8rem;">
                <div style="display:flex; align-items:center; gap:8px; color:#64748B;">
                    <span style="color:#00D9FF; font-size:0.75rem;">🧠</span> Learning Engine
                </div>
                <div style="color:#00D9FF; font-weight:600; font-family:'Share Tech Mono', monospace; text-shadow: var(--glow-cyan);">ADAPTIVE</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Threat Shield
        st.markdown("""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; font-family:'Outfit', sans-serif; font-size:0.8rem;">
                <div style="display:flex; align-items:center; gap:8px; color:#64748B;">
                    <span style="color:#7B61FF; font-size:0.75rem;">🛡️</span> Threat Shield
                </div>
                <div style="color:#7B61FF; font-weight:600; font-family:'Share Tech Mono', monospace; text-shadow: var(--glow-purple);">ARMED</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Core Temp
        st.markdown("""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; font-family:'Outfit', sans-serif; font-size:0.8rem;">
                <div style="display:flex; align-items:center; gap:8px; color:#64748B;">
                    <span style="color:#EC4899; font-size:0.75rem;">🌡️</span> Core Temp.
                </div>
                <div style="color:#EC4899; font-weight:600; font-family:'Share Tech Mono', monospace; text-shadow: 0 0 8px rgba(236,72,153,0.3);">42°C</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Core Temp sparkline path SVG
        st.markdown("""
            <div style="height:25px; width:100%; margin-top:5px; margin-bottom:10px;">
                <svg width="100%" height="25" viewBox="0 0 140 25" style="overflow:visible;">
                    <path d="M 0,15 L 20,12 L 40,18 L 60,10 L 80,14 L 100,6 L 120,16 L 140,8" fill="none" stroke="#EC4899" stroke-width="1.5" style="filter: drop-shadow(0 0 4px #EC4899);"/>
                </svg>
            </div>
        """, unsafe_allow_html=True)
        
        # Core Stability progress bar
        st.markdown('<div class="monitor-label" style="font-size:0.75rem; font-family:\'Share Tech Mono\', monospace; display:flex; justify-content:space-between;"><span>CORE STABILITY</span> <span style="color:#00D9FF;">100%</span></div>', unsafe_allow_html=True)
        st.progress(1.0)
