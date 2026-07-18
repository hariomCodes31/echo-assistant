import streamlit as st
from datetime import datetime, timedelta
from automation.scheduler import _pending, _fired_log, schedule_command, cancel_all

def load_task_scheduler_page():
    st.markdown('<p class="panel-title" style="font-size:1.5rem; color:#00D9FF; letter-spacing:2px; text-transform:uppercase;">⏰ Automation Task Scheduler</p>', unsafe_allow_html=True)
    
    col_config, col_queue = st.columns([5, 5])
    
    # Left Column: Configuration and presets
    with col_config:
        with st.container(border=True):
            st.markdown('<p class="panel-title">Deploy Scheduled Automation</p>', unsafe_allow_html=True)
            
            # Form fields
            cmd_input = st.text_input("Command to Schedule", value="", placeholder="e.g. play lofi girl, open calculator, weather in Tokyo...", key="schedule_cmd_input")
            
            t_col1, t_col2, t_col3 = st.columns([3, 3, 4])
            with t_col1:
                hours = [str(i) for i in range(1, 13)]
                selected_hour = st.selectbox("Hour", options=hours, index=datetime.now().hour % 12 - 1 if datetime.now().hour % 12 != 0 else 11)
            with t_col2:
                minutes = [f"{i:02d}" for i in range(60)]
                selected_minute = st.selectbox("Minute", options=minutes, index=datetime.now().minute)
            with t_col3:
                meridiems = ["AM", "PM"]
                selected_meridiem = st.selectbox("AM/PM", options=meridiems, index=0 if datetime.now().hour < 12 else 1)
                
            if st.button("🚀 Queue Task Timer", use_container_width=True, key="deploy_timer_btn"):
                if cmd_input:
                    time_str = f"{selected_hour}:{selected_minute}{selected_meridiem.lower()}"
                    res = schedule_command(time_str, cmd_input)
                    st.toast(res)
                    st.rerun()
                else:
                    st.toast("⚠️ Please enter a command first")
                    
        with st.container(border=True):
            st.markdown('<p class="panel-title">Relative Quick Presets</p>', unsafe_allow_html=True)
            st.markdown('<div style="font-size:0.7rem; color:#64748B; margin-bottom:10px;">Schedule automation tasks relative to current system time:</div>', unsafe_allow_html=True)
            
            presets = [
                ("🌤️ Weather Check in 1 Min", 1, "weather in delhi"),
                ("🎵 Play Chillhop in 5 Mins", 5, "play chillhop beats"),
                ("🌐 Launch Chrome in 10 Mins", 10, "open chrome"),
                ("🖥️ Take Screenshot in 15 Mins", 15, "take screenshot")
            ]
            
            for label, minutes_delay, command in presets:
                if st.button(label, use_container_width=True, key=f"preset_sched_{minutes_delay}"):
                    target_time = datetime.now() + timedelta(minutes=minutes_delay)
                    time_str = target_time.strftime("%I:%M%p").lower()
                    res = schedule_command(time_str, command)
                    st.toast(res)
                    st.rerun()

    # Right Column: Queue list and history logs
    with col_queue:
        with st.container(border=True):
            st.markdown('<p class="panel-title">Active Timers Queue</p>', unsafe_allow_html=True)
            
            pending_keys = list(_pending.keys())
            
            if pending_keys:
                for label in pending_keys:
                    try:
                        time_part, cmd_part = label.split("::", 1)
                    except ValueError:
                        time_part, cmd_part = "Time Unknown", label
                        
                    card_col, btn_col = st.columns([8, 2])
                    with card_col:
                        st.markdown(f"""<div style="background:rgba(255,255,255,0.01); border-left:3px solid #7B61FF; padding:6px 10px; border-radius:4px; font-family:'Share Tech Mono', monospace; font-size:0.75rem; color:#FFFFFF;">
<b>CMD:</b> {cmd_part}<br>
<span style="color:#00D9FF;"><b>FIRE:</b> {time_part}</span>
</div>""", unsafe_allow_html=True)
                    with btn_col:
                        if st.button("🗑️", key=f"cancel_btn_{label}", help=f"Cancel task at {time_part}", use_container_width=True):
                            timer = _pending.get(label)
                            if timer:
                                timer.cancel()
                            _pending.pop(label, None)
                            st.toast("✅ Task cancelled successfully")
                            st.rerun()
                            
                st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
                if st.button("🛑 Purge All Active Timers", use_container_width=True, type="secondary", key="clear_all_timers_btn"):
                    res = cancel_all()
                    st.toast(res)
                    st.rerun()
            else:
                st.markdown('<div style="text-align:center; color:#64748B; font-family:\'Share Tech Mono\', monospace; font-size:0.75rem; padding: 25px;">📭 Queue Empty. No commands scheduled.</div>', unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown('<p class="panel-title">Fired Telemetry History</p>', unsafe_allow_html=True)
            
            if _fired_log:
                # Render last 5 fired events
                for event in reversed(_fired_log[-5:]):
                    time_val = event.get("time")
                    cmd_val = event.get("command")
                    status_val = event.get("status")
                    detail_val = event.get("detail", "")
                    
                    status_color = "#10B981" if status_val == "Success" else "#EF4444"
                    
                    st.markdown(f"""<div style="background:rgba(255,255,255,0.01); border-bottom:1px solid rgba(255,255,255,0.02); padding:5px 0; font-family:'Share Tech Mono', monospace; font-size:0.7rem; color:#FFFFFF;">
<span style="color:#64748B;">[{time_val}]</span> <b>CMD:</b> {cmd_val}<br>
<b>STATUS:</b> <span style="color:{status_color}; font-weight:bold;">{status_val}</span> | <b>LOG:</b> <span style="color:#94A3B8;">{detail_val[:40] + '...' if len(detail_val) > 40 else detail_val}</span>
</div>""", unsafe_allow_html=True)
            else:
                st.markdown('<div style="text-align:center; color:#64748B; font-family:\'Share Tech Mono\', monospace; font-size:0.75rem; padding: 15px;">No historical telemetry records found.</div>', unsafe_allow_html=True)
