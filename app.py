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

    st.markdown(
        f"<style>{css_content}</style>",
        unsafe_allow_html=True
    )

# Load CSS once (called at module level, NOT inside the function)
load_all_stylesheets()

# Initialize session parameters before injecting styles
if "os_theme" not in st.session_state:
    st.session_state.os_theme = "Cyber Cyan"
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
    st.markdown(custom_style, unsafe_allow_html=True)

# Inject dynamic theme variables
inject_theme_css()

# ── HUD Interactions + Neural Canvas Background ──
# stc.html() required — st.markdown() strips <script> in Streamlit 1.x
stc.html("""
<!DOCTYPE html><html><head>
<style>body{margin:0;padding:0;background:transparent;overflow:hidden;}</style>
</head><body>
<script>
(function() {
  var doc = window.parent.document;
  var win = window.parent;

  // ── Neural network canvas background ──────────────────────────────────────
  if (!doc.getElementById('neural-canvas')) {
    var cvs = doc.createElement('canvas');
    cvs.id = 'neural-canvas';
    Object.assign(cvs.style, {
      position:'fixed', top:'0', left:'0', width:'100%', height:'100%',
      pointerEvents:'none', zIndex:'-1', opacity:'0.55'
    });
    doc.body.insertBefore(cvs, doc.body.firstChild);

    var ctx = cvs.getContext('2d');
    var W, H, nodes = [], NODES=80, LINK=160;
    var mx=0, my=0;

    function resize(){ W=cvs.width=win.innerWidth; H=cvs.height=win.innerHeight; }
    resize();
    win.addEventListener('resize', resize);
    doc.addEventListener('mousemove', function(e){ mx=e.clientX; my=e.clientY; });

    function mkNode(){
      return {
        x:Math.random()*W, y:Math.random()*H,
        z:Math.random()*400,
        vx:(Math.random()-0.5)*0.25,
        vy:(Math.random()-0.5)*0.25,
        vz:(Math.random()-0.5)*0.5,
        hue: Math.random()<0.6 ? 193 : (Math.random()<0.5 ? 260 : 330)
      };
    }
    for(var i=0;i<NODES;i++) nodes.push(mkNode());

    var frame=0;
    function drawNeural(){
      frame++;
      ctx.clearRect(0,0,W,H);

      // Cursor influence
      var inf = 80;
      for(var i=0;i<nodes.length;i++){
        var n=nodes[i];
        var dx=n.x-mx, dy=n.y-my;
        var d=Math.sqrt(dx*dx+dy*dy);
        if(d<inf){ n.vx+=dx/d*0.04; n.vy+=dy/d*0.04; }
        n.x+=n.vx; n.y+=n.vy; n.z+=n.vz;
        n.vx*=0.98; n.vy*=0.98;
        if(n.x<0||n.x>W) n.vx*=-1;
        if(n.y<0||n.y>H) n.vy*=-1;
        if(n.z<0||n.z>400) n.vz*=-1;
      }

      // Draw links
      for(var i=0;i<nodes.length;i++){
        for(var j=i+1;j<nodes.length;j++){
          var dx=nodes[i].x-nodes[j].x, dy=nodes[i].y-nodes[j].y;
          var dist=Math.sqrt(dx*dx+dy*dy);
          if(dist<LINK){
            var alpha=(1-dist/LINK)*0.12*(nodes[i].z/400+0.2);
            ctx.beginPath();
            ctx.moveTo(nodes[i].x,nodes[i].y);
            ctx.lineTo(nodes[j].x,nodes[j].y);
            ctx.strokeStyle='rgba(0,217,255,'+alpha+')';
            ctx.lineWidth=0.6;
            ctx.stroke();
          }
        }
      }

      // Draw nodes
      for(var i=0;i<nodes.length;i++){
        var n=nodes[i];
        var depth=(n.z/400);
        var r=1+depth*2.5;
        var alpha=0.3+depth*0.6;
        ctx.beginPath();
        ctx.arc(n.x,n.y,r,0,Math.PI*2);
        ctx.fillStyle='hsla('+n.hue+',100%,65%,'+alpha+')';
        ctx.fill();
        if(depth>0.5){
          var g=ctx.createRadialGradient(n.x,n.y,0,n.x,n.y,r*5);
          g.addColorStop(0,'hsla('+n.hue+',100%,65%,0.25)');
          g.addColorStop(1,'transparent');
          ctx.beginPath(); ctx.arc(n.x,n.y,r*5,0,Math.PI*2);
          ctx.fillStyle=g; ctx.fill();
        }
      }
      win.requestAnimationFrame(drawNeural);
    }
    drawNeural();
  }

  // ── Cursor glow ───────────────────────────────────────────────────────────
  if (!doc.getElementById('echo-cursor-glow')) {
    var g = doc.createElement('div');
    g.id = 'echo-cursor-glow';
    Object.assign(g.style, {
      position:'fixed', width:'280px', height:'280px', borderRadius:'50%',
      background:'radial-gradient(circle,rgba(0,217,255,0.055) 0%,rgba(123,97,255,0.025) 45%,transparent 70%)',
      pointerEvents:'none', zIndex:'9998', transform:'translate(-50%,-50%)',
      mixBlendMode:'screen', left:'-500px', top:'-500px'
    });
    doc.body.appendChild(g);
  }
  var glow = doc.getElementById('echo-cursor-glow');
  var cx=win.innerWidth/2, cy=win.innerHeight/2, tx=cx, ty=cy;
  function lerp(a,b,t){ return a+(b-a)*t; }
  doc.addEventListener('mousemove', function(e){ tx=e.clientX; ty=e.clientY; });
  (function loop(){
    cx=lerp(cx,tx,0.1); cy=lerp(cy,ty,0.1);
    if(glow){ glow.style.left=cx+'px'; glow.style.top=cy+'px'; }
    win.requestAnimationFrame(loop);
  })();

  // ── 3D card tilt ±6° ─────────────────────────────────────────────────────────
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
</script>
</body></html>
""", height=0, scrolling=False)

# Inject background visual elements (core background, particles, scan lines)
st.markdown("""
    <div class="core-background"></div>

    <!-- Floating Particles -->
    <div class="particles">
        <span class="particle p1"></span>
        <span class="particle p2"></span>
        <span class="particle p3"></span>
        <span class="particle p4"></span>
        <span class="particle p5"></span>
        <span class="particle p6"></span>
        <span class="particle p7"></span>
        <span class="particle p8"></span>
        <span class="particle p9"></span>
        <span class="particle p10"></span>
        <span class="particle p11"></span>
        <span class="particle p12"></span>
    </div>

    <!-- Scan Lines -->
    <div class="scan-lines"></div>
""", unsafe_allow_html=True)

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
col_left, col_mid, col_right = st.columns([2.2, 5.3, 2.5])

# --- LEFT COLUMN: Navigation & Sources ---
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
with col_right:
    # 1. CPU/RAM meters
    render_system_monitor()
    
    # 2. Quick command button grids
    if st.session_state.active_view == "Chats":
        render_quick_tools()
        
    # 3. Active mic trigger waveform panel
    render_voice_panel()