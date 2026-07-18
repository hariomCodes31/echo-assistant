import streamlit as st
import streamlit.components.v1 as stc
# Trigger reload: 2026-07-02T17:40
import base64
import subprocess
from datetime import datetime

from ai import ask_ai
from modules.memory import load_memory, save_memory
from modules.router import execute, execute_multiple
from modules.voice_manager import voice_manager

# Import UI Components and subpages
from components.sidebar import render_sidebar
from components.topbar import render_topbar
from components.system_monitor import render_system_monitor
from components.quick_tools import render_quick_tools
from components.voice_panel import render_voice_panel
from components.bottom_bar import render_bottom_bar

from pages.chat import load_chat_page
from pages.vision import load_vision_page
from pages.voice_settings import load_voice_settings_page
from pages.desktop_actions import load_desktop_actions_page
from pages.browser_tools import load_browser_tools_page
from pages.music_playbacks import load_music_playbacks_page
from pages.weather_alerts import load_weather_alerts_page
from pages.system_control import load_system_control_page
from pages.sports import load_sports_page
from pages.settings import load_settings_page
from pages.task_scheduler import load_task_scheduler_page
from pages.notes import load_notes_page
from pages.calculator import load_calculator_page

# Set page config to wide layout
st.set_page_config(
    page_title="ECHO OS - Quantum Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Helper to load and inject all modular CSS files
def load_all_stylesheets():
    css_files = [
        "assets/css/main.css",
        "assets/css/os_shell.css",
        "assets/css/layout.css",
        "assets/css/components.css",
        "assets/css/glass.css",
        "assets/css/animations.css",
        "assets/css/chat.css",
        "assets/css/ai_core.css",
        "assets/css/cinematic.css",
        "assets/css/3d_depth.css",
        "assets/css/ultraredesign.css",
    ]

    css_content = ""

    for path in css_files:
        try:
            with open(path, "r", encoding="utf-8") as f:
                css_content += f.read() + "\n"
        except FileNotFoundError:
            continue

    # Load operating mode specific CSS overrides
    from modules.theme_engine import ThemeEngine
    active_mode = st.session_state.get("os_mode", "quantum")
    theme_css = ThemeEngine.get_theme_css(active_mode)
    css_content += "\n/* Operating Mode Overrides */\n" + theme_css

    clean_css = "\n".join([line.strip() for line in css_content.split("\n") if line.strip()])
    st.html(f"<style>{clean_css}</style>")




# Load CSS once (called at module level, NOT inside the function)
load_all_stylesheets()

# Initialize session parameters before injecting styles
if "os_theme" not in st.session_state:
    st.session_state.os_theme = "Cyber Cyan"
if "os_mode" not in st.session_state:
    st.session_state.os_mode = "quantum"
if "llm_model" not in st.session_state:
    st.session_state.llm_model = "llama-3.3-70b-versatile"
if "llm_temp" not in st.session_state:
    st.session_state.llm_temp = 0.7
if "llm_max_tokens" not in st.session_state:
    st.session_state.llm_max_tokens = 1024


def inject_theme_css():
    theme = st.session_state.get("os_theme", "Cyber Cyan")
    themes = {
        "Cyber Cyan": ("#00D9FF", "rgba(0, 217, 255, 0.3)"),
        "Neon Green": ("#10B981", "rgba(16, 185, 129, 0.3)"),
        "Synthwave Pink": ("#EC4899", "rgba(236, 72, 153, 0.3)"),
        "Amber Gold": ("#F59E0B", "rgba(245, 158, 11, 0.3)"),
        "Crimson Red": ("#EF4444", "rgba(239, 68, 68, 0.3)"),
        "Grape Purple": ("#8B5CF6", "rgba(139, 92, 246, 0.3)")
    }
    hex_val, rgba_val = themes.get(theme, themes["Cyber Cyan"])
    custom_style = f"""
    <style>
        :root {{
            --neon-cyan: {hex_val} !important;
            --glow-cyan: 0 0 15px {rgba_val} !important;
        }}
    </style>
    """
    clean_style = "\n".join([line.strip() for line in custom_style.split("\n") if line.strip()])
    st.html(clean_style)



# Inject dynamic theme variables
inject_theme_css()

# ── Dynamic Theme Assets & HUD Interactions ──
from modules.theme_engine import ThemeEngine
active_mode = st.session_state.get("os_mode", "quantum")

# 1. Inject theme background elements HTML
bg_html = ThemeEngine.get_theme_background_html(active_mode)
if bg_html is None:
    bg_html = ThemeEngine.get_theme_background_html("quantum")
if bg_html:
    clean_bg = "\n".join([line.strip() for line in bg_html.split("\n") if line.strip()])
    st.html(clean_bg)



# 2. Inject core UI interactions (card tilt, magnetic, ripple) + theme custom JS
theme_js = ThemeEngine.get_theme_js(active_mode)

base_interactions_js = """
(function() {
  var doc = window.parent.document;
  var win = window.parent;

  // ── 3D card tilt ±5° ─────────────────────────────────────────────────────────
  function applyTilt(el) {
    if(el._tiltBound) return; el._tiltBound=true;
    var M=5;
    el.addEventListener('mousemove', function(e){
      var r=el.getBoundingClientRect();
      var x=(e.clientX-r.left)/r.width-0.5, y=(e.clientY-r.top)/r.height-0.5;
      el.style.transform='perspective(900px) rotateX('+(-y*M)+'deg) rotateY('+(x*M)+'deg) translateZ(8px) translateY(-5px)';
      el.style.transition='transform 0.08s ease';
      el.style.zIndex='20';
    });
    el.addEventListener('mouseleave', function(){
      el.style.transform='perspective(900px) rotateX(0deg) rotateY(0deg) translateZ(0) translateY(0)';
      el.style.transition='transform 0.6s cubic-bezier(0.16,1,0.3,1)';
      el.style.zIndex='';
    });
  }

  // ── Magnetic button ──────────────────────────────────────────────────────────
  function applyMagnetic(btn){
    if(btn._magBound) return; btn._magBound=true;
    var P=0.28;
    btn.addEventListener('mousemove',function(e){
      var r=btn.getBoundingClientRect();
      btn.style.transform='perspective(300px) translate('+(( e.clientX-(r.left+r.width/2))*P)+'px,'+(( e.clientY-(r.top+r.height/2))*P)+'px) translateZ(6px) scale(1.03)';
      btn.style.transition='transform 0.12s ease';
    });
    btn.addEventListener('mouseleave',function(){
      btn.style.transform='perspective(300px) translate(0,0) translateZ(0) scale(1)';
      btn.style.transition='transform 0.4s cubic-bezier(0.16,1,0.3,1)';
    });
  }

  // ── Ripple ────────────────────────────────────────────────────────────────────
  if(!doc.getElementById('echo-ripple-style')){
    var s=doc.createElement('style'); s.id='echo-ripple-style';
    s.textContent='@keyframes echo-ripple{0%{transform:scale(0);opacity:0.7}100%{transform:scale(3.5);opacity:0}}';
    doc.head.appendChild(s);
  }
  function applyRipple(btn){
    if(btn._rippleBound) return; btn._rippleBound=true;
    btn.style.position='relative'; btn.style.overflow='hidden';
    btn.addEventListener('click',function(e){
      var r=btn.getBoundingClientRect(), sz=Math.max(r.width,r.height)*1.8;
      var rEl=doc.createElement('span');
      Object.assign(rEl.style,{
        position:'absolute',left:(e.clientX-r.left-sz/2)+'px',top:(e.clientY-r.top-sz/2)+'px',
        width:sz+'px',height:sz+'px',borderRadius:'50%',
        background:'rgba(0,217,255,0.22)',transform:'scale(0)',pointerEvents:'none',
        animation:'echo-ripple 0.55s cubic-bezier(0.16,1,0.3,1) forwards'
      });
      btn.appendChild(rEl);
      setTimeout(function(){ rEl.remove(); },600);
    });
  }

  // ── Bind + rebind on re-renders ───────────────────────────────────────────────
  function bindAll(){
    doc.querySelectorAll('[data-testid="stVerticalBlockBorderWrapper"]').forEach(applyTilt);
    doc.querySelectorAll('div.stButton > button').forEach(function(b){ applyMagnetic(b); applyRipple(b); });
  }
  bindAll();
  new MutationObserver(bindAll).observe(doc.body,{childList:true,subtree:true});
})();
"""

transition_js = f"""
(function() {{
  var doc = window.parent.document;
  var win = window.parent;

  // Create overlay if not present
  if (!doc.getElementById('reboot-overlay')) {{
    var overlay = doc.createElement('div');
    overlay.id = 'reboot-overlay';
    overlay.innerHTML = `
      <div class="reboot-container">
        <div class="reboot-scanner"></div>
        <div class="reboot-title">
          <span>ECHO CORE OS REBOOT</span>
          <span class="reboot-percentage">0%</span>
        </div>
        <div class="reboot-progress-bar">
          <div class="reboot-progress-fill"></div>
        </div>
        <div class="reboot-logs"></div>
      </div>
    `;
    doc.body.appendChild(overlay);
  }}

  var overlay = doc.getElementById('reboot-overlay');
  var activeTheme = '{active_mode}';
  var prevTheme = doc.body.getAttribute('data-theme-id');

  if (prevTheme && prevTheme !== activeTheme) {{
    // Trigger transition overlay
    overlay.classList.add('active');
    overlay.style.opacity = '1';
    overlay.style.pointerEvents = 'all';

    var logBox = overlay.querySelector('.reboot-logs');
    var progressFill = overlay.querySelector('.reboot-progress-fill');
    var percentText = overlay.querySelector('.reboot-percentage');

    logBox.innerHTML = '';
    progressFill.style.width = '0%';
    percentText.textContent = '0%';

    var logs = [
      {{ text: 'SYS INTERRUPT: SWITCH MODE SIGNAL RECEIVED', time: 50 }},
      {{ text: 'SHUTTING DOWN EXISTING COGNITIVE THREADS...', time: 200 }},
      {{ text: 'DE-COUPLING ENERGY ORB REACTOR...', time: 400 }},
      {{ text: 'LOADING HARDWARE PROFILE: ' + activeTheme.toUpperCase(), time: 650 }},
      {{ text: 'INJECTING DESIGN SYSTEM TOKENS...', time: 900 }},
      {{ text: 'SPAWNING PARTICLE ENVIRONMENT LAYER...', time: 1100 }},
      {{ text: 'SYNAPSE RECONNECT COMPLETE // ECHO BOOT SUCCESS', time: 1350 }}
    ];

    logs.forEach(function(log) {{
      setTimeout(function() {{
        var entry = doc.createElement('div');
        entry.className = 'reboot-log-entry success';
        entry.innerHTML = '<span>[OK]</span> <span>' + log.text + '</span>';
        logBox.appendChild(entry);
        logBox.scrollTop = logBox.scrollHeight;
      }}, log.time);
    }});

    var progress = 0;
    var interval = setInterval(function() {{
      progress += 5;
      if (progress > 100) {{
        progress = 100;
        clearInterval(interval);
        setTimeout(function() {{
          overlay.style.opacity = '0';
          overlay.style.pointerEvents = 'none';
          setTimeout(function() {{
            overlay.classList.remove('active');
          }}, 400);
          doc.body.setAttribute('data-theme-id', activeTheme);
        }}, 300);
      }}
      progressFill.style.width = progress + '%';
      percentText.textContent = progress + '%';
    }}, 75);
  }} else {{
    doc.body.setAttribute('data-theme-id', activeTheme);
  }}
}})();
"""


combined_js = f"""
<!DOCTYPE html><html><head>
<style>body{{margin:0;padding:0;background:transparent;overflow:hidden;}}</style>
</head><body>
<script>
{base_interactions_js}
{transition_js}
{theme_js}
</script>
</body></html>
"""
stc.html(combined_js, height=0, scrolling=False)



# Initialize session parameters
if "active_view" not in st.session_state:
    st.session_state.active_view = "Chats"
if "messages" not in st.session_state:
    st.session_state.messages = load_memory()
if "vision_result" not in st.session_state:
    st.session_state.vision_result = ""

# ----------------- UPLOADER STATE SYNC ----------------- #
uploaded_file = None
if st.session_state.get("vision_uploader") is not None:
    uploaded_file = st.session_state.vision_uploader
elif st.session_state.get("vision_uploader_main") is not None:
    uploaded_file = st.session_state.vision_uploader_main

if uploaded_file is not None:
    st.session_state.uploaded_image = uploaded_file.getvalue()
    st.session_state.uploaded_image_mime = uploaded_file.type
    st.session_state.uploaded_image_name = uploaded_file.name
    st.session_state.uploaded_image_size = len(uploaded_file.getvalue())

# ----------------- MAIN OS WORKSPACE GRID ----------------- #
# Layout configurations:
# Quantum: Dashboard [2.2, 5.3, 2.5]
# Vision: Floating dock navigation / windows [2.0, 5.5, 2.5]
# Matrix: Terminal wireframe console [1.5, 7.0, 1.5]
# Cyberpunk: Skewed asymmetrical layout [3.0, 4.5, 2.5]
# Minimal: Command palette only [0.01, 9.98, 0.01] (sidebar and monitor columns hidden)

layout_widths = {
    "minimal": [0.01, 9.98, 0.01],
    "cyberpunk": [3.0, 4.5, 2.5],
    "matrix": [1.5, 7.0, 1.5],
    "vision": [2.0, 5.5, 2.5],
}

widths = layout_widths.get(active_mode, [2.2, 5.3, 2.5])
col_left, col_mid, col_right = st.columns(widths)

# --- LEFT COLUMN: Navigation & Sources ---
if widths[0] > 0.1:
    with col_left:
        render_sidebar()


# --- MIDDLE COLUMN: Clock, Main Workspace, Inputs & Console Reports ---
with col_mid:
    # 1. Top telemetry topbar widgets
    try:
        import psutil
        cpu_val = psutil.cpu_percent(interval=0.1)
        ram_val = psutil.virtual_memory().percent
    except Exception:
        cpu_val = 23
        ram_val = 48
    render_topbar(cpu=cpu_val, ram=ram_val)
    
    # 2. Main Tab router selection
    if st.session_state.active_view == "Chats":
        load_chat_page()
    elif st.session_state.active_view == "Vision":
        load_vision_page()
    elif st.session_state.active_view == "Voice Settings":
        load_voice_settings_page()
    elif st.session_state.active_view == "Desktop Actions":
        load_desktop_actions_page()
    elif st.session_state.active_view == "Browser Tools":
        load_browser_tools_page()
    elif st.session_state.active_view == "Music Playbacks":
        load_music_playbacks_page()
    elif st.session_state.active_view == "Weather Alerts":
        load_weather_alerts_page()
    elif st.session_state.active_view == "System Control":
        load_system_control_page()
    elif st.session_state.active_view == "Sports Hub":
        load_sports_page()
    elif st.session_state.active_view == "Control Settings":
        load_settings_page()
    elif st.session_state.active_view == "Task Scheduler":
        load_task_scheduler_page()
    elif st.session_state.active_view == "Notes":
        load_notes_page()
    elif st.session_state.active_view == "Calculator":
        load_calculator_page()
        
    # 3. Bottom Chat Entry Command input field
    st.markdown('<div style="height: 8px;"></div>', unsafe_allow_html=True)
    prompt = st.chat_input("Type a command or ask anything...")
    
    if prompt:
        # Append query to state (with timestamp)
        ts_now = datetime.now().strftime("%d %b %Y, %I:%M:%S %p")
        user_message = {"role": "user", "content": prompt, "timestamp": ts_now}
        if st.session_state.get("uploaded_image") is not None:
            mime = st.session_state.get("uploaded_image_mime", "image/png")
            b64_data = base64.b64encode(st.session_state.uploaded_image).decode()
            user_message["image"] = f"data:{mime};base64,{b64_data}"
            
        st.session_state.messages.append(user_message)
        
        with st.spinner("Executing query..."):
            responses = execute_multiple(prompt)
            if responses:
                answer = "\n".join(responses)
            else:
                answer = execute(prompt)
                if answer is None:
                    answer = ask_ai(prompt)
                    
        st.session_state.messages.append({"role": "assistant", "content": answer, "timestamp": ts_now})
        save_memory(st.session_state.messages)
        
        # Link vision reports console updates
        if answer and ("[Source:" in answer or "groq vision" in answer.lower()):
            st.session_state.vision_result = answer
            
        # Speak the chat response using current voice settings
        voice_manager.tts_player.speak(answer)
        st.rerun()

    # 4. Bottom details bar
    render_bottom_bar()

# --- RIGHT COLUMN: Telemetry gauges, Shortcuts & Voice Assistant ---
if widths[2] > 0.1:
    with col_right:
        # 1. CPU/RAM meters
        render_system_monitor()
        
        # 2. Quick command button grids
        if st.session_state.active_view == "Chats":
            render_quick_tools()
            
        # 3. Active mic trigger waveform panel
        render_voice_panel()