import streamlit as st
import textwrap


def render_quantum_core():
    """
    Renders a futuristic holographic Quantum System Core stats panel.
    Overhauled to match spaceship cockpits/HUDs, utilizing dynamic SVG sparklines,
    blinking indicator symbols, digital sub-labels, and glowing status tags.
    """
    core_html = textwrap.dedent("""
        <div class="quantum-core-hud" style="position:relative; width:100%; font-family:var(--font-primary);">
            <div class="corner-bracket tl" style="width:10px; height:10px; border-width:2px 0 0 2px;"></div>
            <div class="corner-bracket tr" style="width:10px; height:10px; border-width:2px 2px 0 0;"></div>
            <div class="corner-bracket bl" style="width:10px; height:10px; border-width:0 0 2px 2px;"></div>
            <div class="corner-bracket br" style="width:10px; height:10px; border-width:0 2px 2px 0;"></div>

            <p class="panel-title" style="margin-bottom:15px; letter-spacing:3px;">QUANTUM SYSTEM CORE</p>

            <!-- NEURAL LINK -->
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <div style="display:flex; align-items:center; gap:8px;">
                    <span style="width:6px; height:6px; background:#10B981; border-radius:50%; display:inline-block; animation:status-pulse 1.5s infinite;"></span>
                    <span style="font-family:var(--font-mono); font-size:0.7rem; color:var(--text-secondary); letter-spacing:0.5px;">NEURAL LINK</span>
                </div>
                <div style="font-family:var(--font-display); font-size:0.75rem; font-weight:700; color:#10B981; text-shadow:0 0 8px rgba(16,185,129,0.5);">CONNECTED</div>
            </div>

            <!-- MEMORY BANK -->
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <div style="display:flex; align-items:center; gap:8px;">
                    <span style="width:6px; height:6px; background:#10B981; border-radius:50%; display:inline-block; animation:status-pulse 2s infinite;"></span>
                    <span style="font-family:var(--font-mono); font-size:0.7rem; color:var(--text-secondary); letter-spacing:0.5px;">MEMORY BANK</span>
                </div>
                <div style="font-family:var(--font-display); font-size:0.75rem; font-weight:700; color:#10B981; text-shadow:0 0 8px rgba(16,185,129,0.5);">ONLINE // RAW</div>
            </div>

            <!-- LEARNING ENGINE -->
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <div style="display:flex; align-items:center; gap:8px;">
                    <span style="width:6px; height:6px; background:var(--neon-cyan); border-radius:50%; display:inline-block; animation:status-pulse 1.2s infinite;"></span>
                    <span style="font-family:var(--font-mono); font-size:0.7rem; color:var(--text-secondary); letter-spacing:0.5px;">LEARNING ENGINE</span>
                </div>
                <div style="font-family:var(--font-display); font-size:0.75rem; font-weight:700; color:var(--neon-cyan); text-shadow:var(--glow-cyan-xs);">ADAPTIVE L5</div>
            </div>

            <!-- THREAT SHIELD -->
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <div style="display:flex; align-items:center; gap:8px;">
                    <span style="width:6px; height:6px; background:var(--neon-purple); border-radius:50%; display:inline-block; animation:status-pulse 1.8s infinite;"></span>
                    <span style="font-family:var(--font-mono); font-size:0.7rem; color:var(--text-secondary); letter-spacing:0.5px;">THREAT SHIELD</span>
                </div>
                <div style="font-family:var(--font-display); font-size:0.75rem; font-weight:700; color:var(--neon-purple); text-shadow:var(--glow-purple-xs);">ARMED // SAFE</div>
            </div>

            <!-- CORE TEMP -->
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:5px;">
                <div style="display:flex; align-items:center; gap:8px;">
                    <span style="width:6px; height:6px; background:var(--neon-pink); border-radius:50%; display:inline-block; animation:status-pulse 2.2s infinite;"></span>
                    <span style="font-family:var(--font-mono); font-size:0.7rem; color:var(--text-secondary); letter-spacing:0.5px;">CORE TEMPERATURE</span>
                </div>
                <div style="font-family:var(--font-display); font-size:0.75rem; font-weight:700; color:var(--neon-pink); text-shadow:var(--glow-pink);">42.8°C</div>
            </div>

            <!-- Sparkline Path SVG -->
            <div style="height:25px; width:100%; margin-top:5px; margin-bottom:15px; background:rgba(0,0,0,0.15); border-radius:4px; border:1px solid rgba(236,72,153,0.15); overflow:hidden;">
                <svg width="100%" height="25" viewBox="0 0 140 25" style="overflow:visible;" preserveAspectRatio="none">
                    <path d="M 0,16 L 20,11 L 40,20 L 60,8 L 80,15 L 100,5 L 120,17 L 140,7"
                          fill="none" stroke="var(--neon-pink)" stroke-width="1.5"
                          style="filter: drop-shadow(0 0 4px var(--neon-pink));"/>
                </svg>
            </div>

            <!-- Stability Progress Dials -->
            <div>
                <div class="monitor-label" style="font-size:0.65rem; font-family:var(--font-mono); display:flex; justify-content:space-between; margin-bottom:5px;">
                    <span>CORE MATRIX STABILITY</span>
                    <span style="color:var(--neon-cyan); font-weight:600; text-shadow:var(--glow-cyan-xs);">100% SECURE</span>
                </div>
                <div style="width:100%; height:6px; background:rgba(255,255,255,0.02); border-radius:3px; border:1px solid rgba(255,255,255,0.04); overflow:hidden; position:relative;">
                    <div style="width:100%; height:100%; background:linear-gradient(90deg, var(--neon-cyan), var(--neon-purple)); box-shadow:var(--glow-cyan-xs);"></div>
                </div>
            </div>
        </div>
    """).strip()

    with st.container(border=True):
        st.markdown(core_html, unsafe_allow_html=True)
