import streamlit as st
import textwrap
from datetime import datetime

def render_topbar(cpu=23, ram=48, groq_status="READY"):
    """
    Renders the top OS status bar widget header panels,
    displaying clock, operational states, resource telemetry, and window settings.
    """
    current_time = datetime.now().strftime("%I:%M %p")
    current_date = datetime.now().strftime("%d %b %Y").upper()
    
    topbar_html = textwrap.dedent(f"""
        <div class="status-badge-container" style="grid-template-columns: repeat(5, 1fr);">
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
        </div>
    """).strip()
    
    st.markdown(topbar_html, unsafe_allow_html=True)
