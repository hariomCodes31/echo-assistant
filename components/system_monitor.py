import streamlit as st
import time


def get_system_stats():
    """
    Tries to query active system statistics using psutil.
    Falls back to safe placeholder signals if psutil is unavailable.
    Returns: cpu, ram, disk, net_sent_kb, net_recv_kb, proc_count
    """
    try:
        import psutil

        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent

        # Network I/O delta over ~0.5 s for a live KB/s reading
        net_before = psutil.net_io_counters()
        time.sleep(0.3)
        net_after = psutil.net_io_counters()
        net_sent_kb = max(0.0, (net_after.bytes_sent - net_before.bytes_sent) / 0.3 / 1024)
        net_recv_kb = max(0.0, (net_after.bytes_recv - net_before.bytes_recv) / 0.3 / 1024)

        proc_count = len(psutil.pids())

        return cpu, ram, disk, net_sent_kb, net_recv_kb, proc_count
    except Exception:
        return 23, 48, 57, 0.0, 0.0, 120


def render_system_monitor():
    """
    Renders progress telemetry bars representing active resource usage,
    plus live network I/O speed and running process count.
    """
    cpu, ram, disk, net_sent_kb, net_recv_kb, proc_count = get_system_stats()

    # Format network speeds for display
    def _fmt_speed(kb):
        if kb >= 1024:
            return f"{kb / 1024:.1f} MB/s"
        return f"{kb:.1f} KB/s"

    with st.container(border=True, height=390):
        st.markdown('<p class="panel-title">System Monitor</p>', unsafe_allow_html=True)

        st.markdown(f'<div class="monitor-label">CPU Usage ({cpu}%)</div>', unsafe_allow_html=True)
        st.progress(cpu / 100.0)

        st.markdown(f'<div class="monitor-label" style="margin-top:10px;">RAM Usage ({ram}%)</div>', unsafe_allow_html=True)
        st.progress(ram / 100.0)

        st.markdown(f'<div class="monitor-label" style="margin-top:10px;">Storage Allocation ({disk}%)</div>', unsafe_allow_html=True)
        st.progress(disk / 100.0)

        # ── Network I/O ──────────────────────────────────────────────────────
        st.markdown(
            '<div class="monitor-label" style="margin-top:14px; margin-bottom:4px;">🌐 Network I/O</div>',
            unsafe_allow_html=True,
        )
        net_col1, net_col2 = st.columns(2)
        with net_col1:
            st.markdown(
                f'<div style="font-family:\'Share Tech Mono\',monospace; font-size:0.7rem; '
                f'color:#00D9FF; text-align:center; background:rgba(0,217,255,0.05); '
                f'border:1px solid rgba(0,217,255,0.15); border-radius:6px; padding:4px 6px;">'
                f'↑ {_fmt_speed(net_sent_kb)}</div>',
                unsafe_allow_html=True,
            )
        with net_col2:
            st.markdown(
                f'<div style="font-family:\'Share Tech Mono\',monospace; font-size:0.7rem; '
                f'color:#10B981; text-align:center; background:rgba(16,185,129,0.05); '
                f'border:1px solid rgba(16,185,129,0.15); border-radius:6px; padding:4px 6px;">'
                f'↓ {_fmt_speed(net_recv_kb)}</div>',
                unsafe_allow_html=True,
            )

        # ── Process count ────────────────────────────────────────────────────
        st.markdown(
            f'<div style="margin-top:10px; font-family:\'Share Tech Mono\',monospace; '
            f'font-size:0.7rem; color:#64748B; display:flex; justify-content:space-between;">'
            f'<span>⚙️ Active Processes</span>'
            f'<span style="color:#8B5CF6; font-weight:600;">{proc_count}</span></div>',
            unsafe_allow_html=True,
        )
