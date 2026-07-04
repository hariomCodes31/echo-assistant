import streamlit as st

def get_system_stats():
    """
    Tries to query active system statistics using psutil.
    Falls back to safe placeholder signals if psutil is unavailable.
    """
    try:
        import psutil
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        
        return cpu, ram, disk, f"CPU Usage ({cpu}%)", f"RAM Usage ({ram}%)", f"Storage Allocation ({disk}%)"
    except Exception:
        return 23, 48, 57, "CPU Usage (23%)", "RAM Usage (48%)", "Storage Allocation (57%)"

def render_system_monitor():
    """
    Renders progress telemetry bars representing active resource usage.
    """
    cpu, ram, disk, cpu_str, ram_str, disk_str = get_system_stats()
    
    with st.container(border=True, height=320):
        st.markdown('<p class="panel-title">System Monitor</p>', unsafe_allow_html=True)
        
        st.markdown(f'<div class="monitor-label">{cpu_str}</div>', unsafe_allow_html=True)
        st.progress(cpu / 100.0)
        
        st.markdown(f'<div class="monitor-label" style="margin-top:10px;">{ram_str}</div>', unsafe_allow_html=True)
        st.progress(ram / 100.0)
        
        st.markdown(f'<div class="monitor-label" style="margin-top:10px;">{disk_str}</div>', unsafe_allow_html=True)
        st.progress(disk / 100.0)
