import streamlit as st
import textwrap
import time
from datetime import datetime


def _get_net_speed_str():
    """Return a compact 'up/down KB/s' string using psutil."""
    try:
        import psutil
        before = psutil.net_io_counters()
        time.sleep(0.25)
        after = psutil.net_io_counters()
        sent_kb = max(0.0, (after.bytes_sent - before.bytes_sent) / 0.25 / 1024)
        recv_kb = max(0.0, (after.bytes_recv - before.bytes_recv) / 0.25 / 1024)

        def _fmt(kb):
            return f"{kb / 1024:.1f}M" if kb >= 1024 else f"{kb:.0f}K"

        return f"↑{_fmt(sent_kb)} ↓{_fmt(recv_kb)}"
    except Exception:
        return "↑ -- ↓ --"


def render_topbar(cpu=23, ram=48, groq_status="READY"):
    """
    Renders the top OS status bar widget header panels,
    displaying clock, operational states, resource telemetry, and window settings.
    """
    current_time = datetime.now().strftime("%I:%M %p")
    current_date = datetime.now().strftime("%d %b %Y").upper()
    net_str = _get_net_speed_str()

    topbar_html = textwrap.dedent(f"""
        <div class="status-badge-container" style="grid-template-columns: repeat(6, 1fr);">
            <!-- LOCAL TIME -->
            <div class="status-widget" style="position:relative;">
                <div class="corner-bracket tl" style="width:6px; height:6px; border-width:1px 0 0 1px;"></div>
                <div class="corner-bracket tr" style="width:6px; height:6px; border-width:1px 1px 0 0;"></div>
                <div class="corner-bracket bl" style="width:6px; height:6px; border-width:0 0 1px 1px;"></div>
                <div class="corner-bracket br" style="width:6px; height:6px; border-width:0 1px 1px 0;"></div>
                <p style="letter-spacing:1.5px;">SYSTEM CHRONO</p>
                <h4 style="font-family:var(--font-display); letter-spacing:1px;">{current_time}</h4>
                <div style="font-family:var(--font-mono); font-size:0.55rem; color:var(--text-muted); margin-top:3px;">
                    DATE: {current_date} <span style="animation:glow-flicker 1.5s infinite; color:var(--neon-cyan);">⚡</span>
                </div>
            </div>

            <!-- SYSTEM STATE -->
            <div class="status-widget" style="position:relative;">
                <div class="corner-bracket tl" style="width:6px; height:6px; border-width:1px 0 0 1px;"></div>
                <div class="corner-bracket tr" style="width:6px; height:6px; border-width:1px 1px 0 0;"></div>
                <div class="corner-bracket bl" style="width:6px; height:6px; border-width:0 0 1px 1px;"></div>
                <div class="corner-bracket br" style="width:6px; height:6px; border-width:0 1px 1px 0;"></div>
                <p style="letter-spacing:1.5px;">SYS MATRIX</p>
                <h4 style="color:#10B981; text-shadow:0 0 8px rgba(16,185,129,0.4); display:flex; align-items:center; justify-content:center; gap:5px; font-family:var(--font-display);">
                    ONLINE <span class="status-dot-active" style="width:6px; height:6px; background:#10B981; border-radius:50%;"></span>
                </h4>
                <div style="font-family:var(--font-mono); font-size:0.55rem; color:var(--text-muted); margin-top:3px;">SECURE // ACTIVE</div>
            </div>

            <!-- CPU USAGE -->
            <div class="status-widget" style="position:relative;">
                <div class="corner-bracket tl" style="width:6px; height:6px; border-width:1px 0 0 1px;"></div>
                <div class="corner-bracket tr" style="width:6px; height:6px; border-width:1px 1px 0 0;"></div>
                <div class="corner-bracket bl" style="width:6px; height:6px; border-width:0 0 1px 1px;"></div>
                <div class="corner-bracket br" style="width:6px; height:6px; border-width:0 1px 1px 0;"></div>
                <p style="letter-spacing:1.5px;">CORE LOAD</p>
                <h4 style="font-family:var(--font-display);">{cpu}%</h4>
                <div style="font-family:var(--font-mono); font-size:0.55rem; color:var(--text-muted); margin-top:3px;">
                    TEMP: 42°C <span style="color:var(--neon-pink);">■</span>
                </div>
            </div>

            <!-- RAM USAGE -->
            <div class="status-widget" style="position:relative;">
                <div class="corner-bracket tl" style="width:6px; height:6px; border-width:1px 0 0 1px;"></div>
                <div class="corner-bracket tr" style="width:6px; height:6px; border-width:1px 1px 0 0;"></div>
                <div class="corner-bracket bl" style="width:6px; height:6px; border-width:0 0 1px 1px;"></div>
                <div class="corner-bracket br" style="width:6px; height:6px; border-width:0 1px 1px 0;"></div>
                <p style="letter-spacing:1.5px;">MEM BUFFER</p>
                <h4 style="font-family:var(--font-display);">{ram}%</h4>
                <div style="font-family:var(--font-mono); font-size:0.55rem; color:var(--text-muted); margin-top:3px;">ALLOC: STATIC</div>
            </div>

            <!-- GROQ INFERENCE -->
            <div class="status-widget" style="position:relative;">
                <div class="corner-bracket tl" style="width:6px; height:6px; border-width:1px 0 0 1px;"></div>
                <div class="corner-bracket tr" style="width:6px; height:6px; border-width:1px 1px 0 0;"></div>
                <div class="corner-bracket bl" style="width:6px; height:6px; border-width:0 0 1px 1px;"></div>
                <div class="corner-bracket br" style="width:6px; height:6px; border-width:0 1px 1px 0;"></div>
                <p style="letter-spacing:1.5px;">GROQ ENGINE</p>
                <h4 style="color:#EC4899; text-shadow:0 0 8px rgba(236,72,153,0.4); display:flex; align-items:center; justify-content:center; gap:5px; font-family:var(--font-display);">
                    {groq_status} <span class="status-dot-active" style="width:6px; height:6px; background:#EC4899; border-radius:50%;"></span>
                </h4>
                <div style="font-family:var(--font-mono); font-size:0.55rem; color:var(--text-muted); margin-top:3px;">INFERENCE // L1</div>
            </div>

            <!-- NETWORK SPEED -->
            <div class="status-widget" style="position:relative;">
                <div class="corner-bracket tl" style="width:6px; height:6px; border-width:1px 0 0 1px;"></div>
                <div class="corner-bracket tr" style="width:6px; height:6px; border-width:1px 1px 0 0;"></div>
                <div class="corner-bracket bl" style="width:6px; height:6px; border-width:0 0 1px 1px;"></div>
                <div class="corner-bracket br" style="width:6px; height:6px; border-width:0 1px 1px 0;"></div>
                <p style="letter-spacing:1.5px;">COMM CHANNEL</p>
                <h4 style="color:#00D9FF; font-size:0.8rem; font-family:var(--font-mono); font-weight:600; text-shadow:var(--glow-cyan-xs);">{net_str}</h4>
                <div style="font-family:var(--font-mono); font-size:0.55rem; color:var(--text-muted); margin-top:3px;">BANDWIDTH: MAX 📶</div>
            </div>
        </div>
    """).strip()

    st.markdown(topbar_html, unsafe_allow_html=True)

