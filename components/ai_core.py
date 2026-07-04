import streamlit as st
from textwrap import dedent


STATE_MAP = {
    "Idle": "core-idle",
    "Listening": "core-listening",
    "Processing": "core-processing",
    "Speaking": "core-speaking",
}


def render_ai_core(mic_state="Idle"):
    """
    Renders the holographic AI core animation using st.components.v1.html()
    instead of st.markdown() to ensure complex nested HTML + CSS renders properly.
    """
    state = STATE_MAP.get(mic_state, "core-idle")

    full_html = dedent(f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&display=swap');

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            background: transparent;
            overflow: hidden;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            width: 100%;
        }}

        .echo-core {{
            position: relative;
            width: 100%;
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            overflow: hidden;
            isolation: isolate;
        }}

        /* Background radial glow */
        .core-background {{
            position: absolute;
            inset: 0;
            background: radial-gradient(circle at center, rgba(0,217,255,.08), transparent 70%);
        }}

        /* Floating stars */
        .core-stars {{
            position: absolute;
            inset: 0;
        }}
        .core-stars span {{
            position: absolute;
            width: 3px;
            height: 3px;
            border-radius: 50%;
            background: #00d9ff;
            box-shadow: 0 0 8px #00d9ff, 0 0 16px #00d9ff;
            animation: floatStars linear infinite;
        }}
        .s1 {{ top:8%; left:18%; animation-duration:15s; }}
        .s2 {{ top:16%; left:73%; animation-duration:20s; }}
        .s3 {{ top:31%; left:9%; animation-duration:14s; }}
        .s4 {{ top:39%; left:82%; animation-duration:18s; }}
        .s5 {{ top:51%; left:16%; animation-duration:12s; }}
        .s6 {{ top:63%; left:72%; animation-duration:16s; }}
        .s7 {{ top:76%; left:28%; animation-duration:19s; }}
        .s8 {{ top:83%; left:61%; animation-duration:15s; }}
        .s9 {{ top:21%; left:41%; animation-duration:22s; }}
        .s10 {{ top:52%; left:52%; animation-duration:18s; }}
        .s11 {{ top:71%; left:86%; animation-duration:17s; }}
        .s12 {{ top:12%; left:58%; animation-duration:14s; }}

        /* Vertical beam */
        .vertical-beam {{
            position: absolute;
            width: 4px;
            height: 55%;
            background: linear-gradient(transparent, rgba(0,217,255,.8), transparent);
            filter: blur(4px);
            animation: beamPulse 2.8s infinite;
        }}

        /* Platform rings */
        .projector-platform {{
            position: absolute;
            width: min(380px, 90%);
            height: min(380px, 90%);
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        .platform-ring {{
            position: absolute;
            border-radius: 50%;
            border: 1px solid rgba(0,217,255,.12);
        }}
        .ring1 {{ width:100%; height:100%; }}
        .ring2 {{ width:83%; height:83%; }}
        .ring3 {{ width:66%; height:66%; }}
        .ring4 {{ width:46%; height:46%; }}
        .ring5 {{ width:32%; height:32%; }}

        /* Core area */
        .core-area {{
            position: relative;
            width: min(380px, 90%);
            height: min(380px, 90%);
            display: flex;
            justify-content: center;
            align-items: center;
        }}

        /* Orbits */
        .orbit {{
            position: absolute;
            border-radius: 50%;
            border: 1px solid rgba(0,217,255,.15);
        }}
        .orbit1 {{ width:95%; height:95%; animation: spinClock 30s linear infinite; }}
        .orbit2 {{ width:80%; height:80%; animation: spinAnti 22s linear infinite; }}
        .orbit3 {{ width:65%; height:65%; animation: spinClock 16s linear infinite; }}
        .orbit4 {{ width:50%; height:50%; animation: spinAnti 12s linear infinite; }}
        .orbit5 {{ width:38%; height:38%; animation: spinClock 9s linear infinite; }}

        /* Satellites */
        .satellite {{
            position: absolute;
            width: 5px;
            height: 5px;
            border-radius: 50%;
            background: #00d9ff;
            box-shadow: 0 0 6px #00d9ff, 0 0 14px #00d9ff;
        }}
        .sat1 {{ top:5%; left:48%; animation: spinClock 15s linear infinite; }}
        .sat2 {{ top:48%; right:3%; animation: spinAnti 12s linear infinite; }}
        .sat3 {{ bottom:8%; left:38%; animation: spinClock 18s linear infinite; }}
        .sat4 {{ top:28%; left:5%; animation: spinAnti 14s linear infinite; }}

        /* Spinning circles */
        .outer-circle {{
            position: absolute;
            width: 88%;
            height: 88%;
            border-radius: 50%;
            border: 2px solid rgba(0,217,255,.25);
            animation: spinClock 24s linear infinite;
        }}
        .middle-circle {{
            position: absolute;
            width: 66%;
            height: 66%;
            border-radius: 50%;
            border: 2px dashed rgba(123,97,255,.4);
            animation: spinAnti 18s linear infinite;
        }}
        .inner-circle {{
            position: absolute;
            width: 44%;
            height: 44%;
            border-radius: 50%;
            border: 1px solid rgba(255,255,255,.3);
            animation: spinClock 8s linear infinite;
        }}

        /* Pulse rings */
        .pulse {{
            position: absolute;
            border-radius: 50%;
            border: 2px solid rgba(0,217,255,.4);
        }}
        .pulse1 {{
            width: 30%;
            height: 30%;
            animation: pulseRing 2s infinite;
        }}
        .pulse2 {{
            width: 30%;
            height: 30%;
            animation: pulseRing 2s infinite .8s;
        }}

        /* Energy grid overlay */
        .energy-grid {{
            position: absolute;
            inset: 10%;
            background-image:
                linear-gradient(rgba(0,217,255,.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0,217,255,.03) 1px, transparent 1px);
            background-size: 18px 18px;
            border-radius: 50%;
            opacity: 0.3;
        }}

        /* Core glow */
        .core-glow {{
            position: absolute;
            width: 28%;
            height: 28%;
            border-radius: 50%;
            background: radial-gradient(circle, #00d9ff, #2456ff 70%, transparent);
            filter: blur(30px);
            animation: breathe 3s ease-in-out infinite;
        }}

        /* Core center sphere */
        .core-center {{
            position: absolute;
            width: 22%;
            height: 22%;
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            background: radial-gradient(circle, #ffffff, #00d9ff);
            box-shadow: 0 0 25px #00d9ff, 0 0 60px #00d9ff, 0 0 120px rgba(0,217,255,.45);
        }}

        /* X letter */
        .core-x {{
            font-family: 'Orbitron', sans-serif;
            font-size: clamp(28px, 5vw, 48px);
            font-weight: 900;
            color: white;
            text-shadow: 0 0 10px #00d9ff, 0 0 25px #00d9ff, 0 0 50px #00d9ff;
        }}

        /* State-specific overrides */
        .core-listening .outer-circle {{ animation-duration: 6s; }}
        .core-listening .core-glow {{ animation-duration: 1.2s; }}
        .core-processing .outer-circle {{ animation-duration: 2s; animation-direction: reverse; }}
        .core-processing .core-glow {{ animation-duration: 0.6s; }}
        .core-speaking .core-center {{ animation: speakingVibrate 0.2s ease-in-out infinite; }}

        /* Keyframes */
        @keyframes spinClock {{
            from {{ transform: rotate(0deg); }}
            to {{ transform: rotate(360deg); }}
        }}
        @keyframes spinAnti {{
            from {{ transform: rotate(360deg); }}
            to {{ transform: rotate(0deg); }}
        }}
        @keyframes breathe {{
            0%, 100% {{ transform: scale(.95); opacity: .7; }}
            50% {{ transform: scale(1.08); opacity: 1; }}
        }}
        @keyframes beamPulse {{
            0%, 100% {{ opacity: .35; }}
            50% {{ opacity: 1; }}
        }}
        @keyframes pulseRing {{
            0% {{ transform: scale(1); opacity: 1; }}
            100% {{ transform: scale(2); opacity: 0; }}
        }}
        @keyframes floatStars {{
            0% {{ transform: translateY(0) translateX(0); opacity: 0.3; }}
            50% {{ transform: translateY(-20px) translateX(10px); opacity: 0.7; }}
            100% {{ transform: translateY(0) translateX(0); opacity: 0.3; }}
        }}
        @keyframes speakingVibrate {{
            0%, 100% {{ transform: scale(1.0); }}
            33% {{ transform: scale(1.03) translate(-1px, 1px); }}
            66% {{ transform: scale(0.98) translate(1px, -1px); }}
        }}
    </style>
    </head>
    <body>
        <div class="echo-core {state}">
            <div class="core-background"></div>

            <div class="core-stars">
                <span class="s s1"></span>
                <span class="s s2"></span>
                <span class="s s3"></span>
                <span class="s s4"></span>
                <span class="s s5"></span>
                <span class="s s6"></span>
                <span class="s s7"></span>
                <span class="s s8"></span>
                <span class="s s9"></span>
                <span class="s s10"></span>
                <span class="s s11"></span>
                <span class="s s12"></span>
            </div>

            <div class="vertical-beam"></div>

            <div class="projector-platform">
                <div class="platform-ring ring1"></div>
                <div class="platform-ring ring2"></div>
                <div class="platform-ring ring3"></div>
                <div class="platform-ring ring4"></div>
                <div class="platform-ring ring5"></div>
            </div>

            <div class="core-area">
                <div class="orbit orbit1"></div>
                <div class="orbit orbit2"></div>
                <div class="orbit orbit3"></div>
                <div class="orbit orbit4"></div>
                <div class="orbit orbit5"></div>

                <div class="satellite sat1"></div>
                <div class="satellite sat2"></div>
                <div class="satellite sat3"></div>
                <div class="satellite sat4"></div>

                <div class="outer-circle"></div>
                <div class="middle-circle"></div>
                <div class="inner-circle"></div>

                <div class="pulse pulse1"></div>
                <div class="pulse pulse2"></div>

                <div class="energy-grid"></div>
                <div class="core-glow"></div>

                <div class="core-center">
                    <div class="core-x">X</div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """)

    st.iframe(full_html, height=420)