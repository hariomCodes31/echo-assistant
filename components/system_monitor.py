import streamlit as st
import time
import textwrap


def get_system_stats():
    """
    Query active system statistics using psutil with fallback placeholders.
    Returns: cpu, ram, disk, net_sent_kb, net_recv_kb, proc_count
    """
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent

        net_before = psutil.net_io_counters()
        time.sleep(0.15)
        net_after = psutil.net_io_counters()
        net_sent_kb = max(0.0, (net_after.bytes_sent - net_before.bytes_sent) / 0.15 / 1024)
        net_recv_kb = max(0.0, (net_after.bytes_recv - net_before.bytes_recv) / 0.15 / 1024)

        proc_count = len(psutil.pids())
        return cpu, ram, disk, net_sent_kb, net_recv_kb, proc_count
    except Exception:
        return 18.5, 52.4, 38.1, 14.2, 125.8, 142


def render_system_monitor():
    """
    Futuristic HUD Telemetry:
    - Side-by-side circular SVG gauges for CPU and RAM with glow rings.
    - Linear holographic scale for Storage.
    - Animated signal waveform for Network I/O.
    - Process counts displayed with live digital readout frames.
    """
    cpu, ram, disk, net_sent_kb, net_recv_kb, proc_count = get_system_stats()

    def _fmt_speed(kb):
        if kb >= 1024:
            return f"{kb / 1024:.1f} MB/s"
        return f"{kb:.1f} KB/s"

    # SVG Circle details
    # Radius = 30, Circumference = ~188.4
    cpu_dash = (cpu / 100.0) * 188.4
    ram_dash = (ram / 100.0) * 188.4

    monitor_html = textwrap.dedent(f"""
        <div class="system-monitor-hud" style="position:relative; width:100%; font-family:var(--font-primary);">
            <div class="corner-bracket tl" style="width:10px; height:10px; border-width:2px 0 0 2px;"></div>
            <div class="corner-bracket tr" style="width:10px; height:10px; border-width:2px 2px 0 0;"></div>
            <div class="corner-bracket bl" style="width:10px; height:10px; border-width:0 0 2px 2px;"></div>
            <div class="corner-bracket br" style="width:10px; height:10px; border-width:0 2px 2px 0;"></div>

            <p class="panel-title" style="margin-bottom:15px; letter-spacing:3px;">SYSTEM DIAGNOSTIC</p>

            <!-- Circular Telemetry Row -->
            <div style="display:flex; justify-content:space-around; align-items:center; margin-bottom:20px; gap:10px;">
                <!-- CPU GAUGE -->
                <div style="text-align:center; position:relative; width:90px; height:90px; transform-style:preserve-3d; transform:translateZ(10px);">
                    <svg width="90" height="90" viewBox="0 0 80 80" style="transform:rotate(-90deg); overflow:visible;">
                        <!-- Track -->
                        <circle cx="40" cy="40" r="30" fill="none" stroke="rgba(0, 217, 255, 0.05)" stroke-width="5"/>
                        <!-- Indicator -->
                        <circle cx="40" cy="40" r="30" fill="none" stroke="url(#cpuGrad)" stroke-width="5"
                                stroke-dasharray="188.4" stroke-dashoffset="{188.4 - cpu_dash}"
                                stroke-linecap="round" style="filter:drop-shadow(0 0 5px rgba(0,217,255,0.6)); transition: stroke-dashoffset 0.5s ease;"/>
                        <!-- Defs for Gradient -->
                        <defs>
                            <linearGradient id="cpuGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stop-color="var(--neon-cyan)"/>
                                <stop offset="100%" stop-color="var(--neon-blue)"/>
                            </linearGradient>
                        </defs>
                    </svg>
                    <!-- Readout -->
                    <div style="position:absolute; top:50%; left:50%; transform:translate(-50%, -50%); text-align:center;">
                        <span style="font-family:var(--font-display); font-size:0.95rem; font-weight:700; color:var(--text-primary);">{int(cpu)}%</span>
                        <p style="font-size:0.5rem; color:var(--text-muted); margin:0; letter-spacing:1px;">CPU</p>
                    </div>
                </div>

                <!-- RAM GAUGE -->
                <div style="text-align:center; position:relative; width:90px; height:90px; transform-style:preserve-3d; transform:translateZ(10px);">
                    <svg width="90" height="90" viewBox="0 0 80 80" style="transform:rotate(-90deg); overflow:visible;">
                        <!-- Track -->
                        <circle cx="40" cy="40" r="30" fill="none" stroke="rgba(123, 97, 255, 0.05)" stroke-width="5"/>
                        <!-- Indicator -->
                        <circle cx="40" cy="40" r="30" fill="none" stroke="url(#ramGrad)" stroke-width="5"
                                stroke-dasharray="188.4" stroke-dashoffset="{188.4 - ram_dash}"
                                stroke-linecap="round" style="filter:drop-shadow(0 0 5px rgba(123,97,255,0.6)); transition: stroke-dashoffset 0.5s ease;"/>
                        <!-- Defs for Gradient -->
                        <defs>
                            <linearGradient id="ramGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stop-color="var(--neon-purple)"/>
                                <stop offset="100%" stop-color="var(--neon-pink)"/>
                            </linearGradient>
                        </defs>
                    </svg>
                    <!-- Readout -->
                    <div style="position:absolute; top:50%; left:50%; transform:translate(-50%, -50%); text-align:center;">
                        <span style="font-family:var(--font-display); font-size:0.95rem; font-weight:700; color:var(--text-primary);">{int(ram)}%</span>
                        <p style="font-size:0.5rem; color:var(--text-muted); margin:0; letter-spacing:1px;">RAM</p>
                    </div>
                </div>
            </div>

            <!-- STORAGE scale (Linear HUD graphic) -->
            <div style="margin-bottom:18px;">
                <div class="monitor-label" style="font-size:0.65rem; letter-spacing:1px; margin-bottom:5px;">
                    <span>STORAGE ALLOCATION</span>
                    <span style="color:var(--neon-cyan); font-weight:600;">{disk}%</span>
                </div>
                <div style="width:100%; height:6px; background:rgba(255,255,255,0.02); border-radius:3px; border:1px solid rgba(255,255,255,0.05); overflow:hidden; position:relative;">
                    <div style="width:{disk}%; height:100%; background:linear-gradient(90deg, var(--neon-cyan), var(--neon-purple)); box-shadow:var(--glow-cyan-xs); border-radius:3px;"></div>
                </div>
            </div>

            <!-- NETWORK INFO (animated sparkline waveform) -->
            <div style="margin-bottom:15px; background:rgba(0,0,0,0.2); border:1px solid rgba(0,217,255,0.1); border-radius:8px; padding:10px;">
                <div class="monitor-label" style="font-size:0.65rem; color:var(--text-muted); margin-bottom:8px; letter-spacing:1.5px;">COMM NET I/O</div>
                <div style="display:flex; justify-content:space-between; gap:10px; margin-bottom:8px;">
                    <div style="font-family:var(--font-mono); font-size:0.62rem; color:var(--neon-cyan);">
                        TX: <span style="font-weight:600;">{_fmt_speed(net_sent_kb)}</span>
                    </div>
                    <div style="font-family:var(--font-mono); font-size:0.62rem; color:var(--neon-green);">
                        RX: <span style="font-weight:600;">{_fmt_speed(net_recv_kb)}</span>
                    </div>
                </div>
                <!-- Mini Signal Waveform Animation -->
                <div style="height:20px; overflow:hidden;">
                    <svg width="100%" height="20" viewBox="0 0 160 20" style="overflow:visible;">
                        <path d="M0,10 L15,10 L25,2 L35,18 L45,10 L75,10 L85,4 L95,16 L105,10 L125,10 L135,1 L145,19 L160,10"
                              fill="none" stroke="rgba(0, 217, 255, 0.45)" stroke-width="1.5"
                              style="filter:drop-shadow(0 0 2px var(--neon-cyan)); stroke-dasharray:600; animation: signalFlow 8s linear infinite;"/>
                    </svg>
                </div>
            </div>

            <!-- PROCESS MANAGER -->
            <div style="display:flex; justify-content:space-between; align-items:center; background:rgba(123,97,255,0.05); border:1px solid rgba(123,97,255,0.15); border-radius:8px; padding:8px 12px;">
                <div style="font-family:var(--font-mono); font-size:0.65rem; color:var(--text-secondary); letter-spacing:1px;">
                    <span style="animation:glow-flicker 2s infinite; color:var(--neon-purple); margin-right:4px;">●</span> ACTIVE PROCESS THREADS
                </div>
                <div style="font-family:var(--font-display); font-size:0.9rem; font-weight:700; color:var(--neon-purple); text-shadow:var(--glow-purple-xs);">{proc_count}</div>
            </div>
        </div>

        <style>
            @keyframes signalFlow {{
                0% {{ stroke-dashoffset: 600; }}
                100% {{ stroke-dashoffset: 0; }}
            }}
        </style>
    """).strip()

    with st.container(border=True):
        st.markdown(monitor_html, unsafe_allow_html=True)
