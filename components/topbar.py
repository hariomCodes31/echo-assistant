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
            <div class="status-widget">
                <p>LOCAL TIME</p>
                <h4>{current_time}</h4>
                <div style="font-size:0.6rem; color:#64748B; margin-top:2px;">{current_date}</div>
            </div>
            <div class="status-widget">
                <p>SYSTEM STATE</p>
                <h4 style="color:#10B981; display:flex; align-items:center; justify-content:center; gap:5px;">
                    ONLINE <span class="status-dot-active" style="width:6px; height:6px; background:#10B981; border-radius:50%; display:inline-block;"></span>
                </h4>
                <div style="font-size:0.6rem; color:#64748B; margin-top:2px;">All Systems Operational</div>
            </div>
            <div class="status-widget">
                <p>CPU USAGE</p>
                <h4>{cpu}%</h4>
                <div style="font-size:0.6rem; color:#64748B; margin-top:2px;">Dynamic Workload</div>
            </div>
            <div class="status-widget">
                <p>RAM USAGE</p>
                <h4>{ram}%</h4>
                <div style="font-size:0.6rem; color:#64748B; margin-top:2px;">Memory Buffer Allocation</div>
            </div>
            <div class="status-widget">
                <p>GROQ SYSTEM</p>
                <h4 style="color:#EC4899; display:flex; align-items:center; justify-content:center; gap:5px;">
                    {groq_status} <span class="status-dot-active" style="width:6px; height:6px; background:#EC4899; border-radius:50%; display:inline-block;"></span>
                </h4>
                <div style="font-size:0.6rem; color:#64748B; margin-top:2px;">Ultra-Fast Inference</div>
            </div>
            <div class="status-widget">
                <p>NETWORK I/O</p>
                <h4 style="color:#00D9FF; font-size:0.85rem; letter-spacing:0.5px;">{net_str}</h4>
                <div style="font-size:0.6rem; color:#64748B; margin-top:2px;">Live Transfer Speed</div>
            </div>
        </div>
    """).strip()

    st.markdown(topbar_html, unsafe_allow_html=True)

