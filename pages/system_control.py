import streamlit as st
import psutil
from datetime import datetime

def get_process_list(filter_name=""):
    processes = []
    for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            info = proc.info
            name = info.get("name") or "unknown"
            if filter_name and filter_name.lower() not in name.lower():
                continue
            processes.append({
                "pid": info["pid"],
                "name": name,
                "cpu": info.get("cpu_percent") or 0.0,
                "mem": info.get("memory_percent") or 0.0
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    # Sort processes by CPU usage first, then Memory
    processes = sorted(processes, key=lambda x: (x["cpu"], x["mem"]), reverse=True)
    return processes

def load_system_control_page():
    st.markdown('<p class="panel-title" style="font-size:1.5rem; color:#00D9FF; letter-spacing:2px; text-transform:uppercase;">⚙️ System Control Center</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([5, 5])
    
    with col1:
        with st.container(border=True):
            st.markdown('<p class="panel-title">Task Terminate Tool</p>', unsafe_allow_html=True)
            
            kill_method = st.radio("End Task By", options=["Process PID", "Process Name"])
            if kill_method == "Process PID":
                pid_input = st.number_input("Enter Process PID", min_value=1, value=1, step=1, key="kill_pid_input")
                if st.button("🔴 Kill Process by PID", use_container_width=True, key="kill_by_pid_btn"):
                    try:
                        p = psutil.Process(pid_input)
                        p.kill()
                        st.success(f"✅ Terminated process {pid_input} ({p.name()})")
                    except Exception as e:
                        st.error(f"❌ Failed to terminate: {e}")
            else:
                name_input = st.text_input("Enter Process Name", value="", placeholder="e.g. chrome.exe, spotify.exe...", key="kill_name_input")
                if st.button("🔴 Kill Processes by Name", use_container_width=True, key="kill_by_name_btn"):
                    if name_input:
                        killed_count = 0
                        for proc in psutil.process_iter(["name"]):
                            try:
                                if proc.info["name"] and proc.info["name"].lower() == name_input.lower():
                                    proc.kill()
                                    killed_count += 1
                            except Exception:
                                pass
                        if killed_count > 0:
                            st.success(f"✅ Terminated {killed_count} instances of '{name_input}'")
                        else:
                            st.warning(f"⚠️ No active process named '{name_input}' was found.")
                    else:
                        st.toast("⚠️ Please enter a process name first")
                        
        with st.container(border=True):
            st.markdown('<p class="panel-title">Core Resource Telemetry</p>', unsafe_allow_html=True)
            
            # Fetch resources
            try:
                boot_time = datetime.fromtimestamp(psutil.boot_time())
                uptime = datetime.now() - boot_time
                hours, remainder = divmod(int(uptime.total_seconds()), 3600)
                minutes, _ = divmod(remainder, 60)
                uptime_str = f"{hours}h {minutes}m"
            except Exception:
                uptime_str = "Unknown"
                
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            st.markdown(f"""
                <div style="font-family:'Share Tech Mono', monospace; font-size:0.8rem; line-height:1.6; color:#64748B;">
                    SYSTEM UPTIME: <span style="color:#7B61FF; font-weight:600;">{uptime_str}</span><br>
                    TOTAL RAM: <span style="color:#00D9FF; font-weight:600;">{mem.total / (1024**3):.1f} GB</span><br>
                    USED RAM: <span style="color:#EC4899; font-weight:600;">{mem.used / (1024**3):.1f} GB ({mem.percent}%)</span><br>
                    TOTAL STORAGE: <span style="color:#00D9FF; font-weight:600;">{disk.total / (1024**3):.1f} GB</span><br>
                    USED STORAGE: <span style="color:#10B981; font-weight:600;">{disk.used / (1024**3):.1f} GB ({disk.percent}%)</span>
                </div>
            """, unsafe_allow_html=True)

    with col2:
        with st.container(border=True):
            st.markdown('<p class="panel-title">Active Process Monitor</p>', unsafe_allow_html=True)
            
            search_proc = st.text_input("Filter Processes", value="", placeholder="Search by name...", key="search_proc_input")
            
            # Get list
            processes = get_process_list(filter_name=search_proc)
            
            # Display list as a neat table
            if processes:
                # Render table headers
                st.markdown("""
                    <div style="display:grid; grid-template-columns: 1.5fr 3fr 1.5fr 1.5fr; font-family:'Share Tech Mono', monospace; font-size:0.75rem; border-bottom: 2px solid rgba(0, 217, 255, 0.2); padding-bottom:4px; font-weight:bold; color:#00D9FF; margin-bottom:5px;">
                        <div>PID</div>
                        <div>NAME</div>
                        <div>CPU%</div>
                        <div>MEM%</div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Show top 12 processes
                for p in processes[:12]:
                    st.markdown(f"""
                        <div style="display:grid; grid-template-columns: 1.5fr 3fr 1.5fr 1.5fr; font-family:'Share Tech Mono', monospace; font-size:0.7rem; border-bottom: 1px solid rgba(255,255,255,0.02); padding: 3px 0; color:#FFFFFF;">
                            <div style="color:#7B61FF;">{p['pid']}</div>
                            <div style="overflow:hidden; text-overflow:ellipsis; white-space:nowrap; padding-right:4px;">{p['name']}</div>
                            <div style="color:#10B981;">{p['cpu']:.1f}%</div>
                            <div style="color:#EC4899;">{p['mem']:.1f}%</div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown('<div style="text-align:center; color:#64748B; font-size:0.75rem; padding: 20px;">No matching processes found.</div>', unsafe_allow_html=True)
