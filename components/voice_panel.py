import streamlit as st
import textwrap
from modules.voice_manager import voice_manager


def render_voice_panel():
    """
    Renders the active Voice Assistant panel with spaceship audio control graphics,
    pulsing state indicators, ALT+SPACE sub-labels, and interactive voice visualizer.
    """
    with st.container(border=True):
        mic_state = voice_manager.mic_state
        state_tag = "idle-wave"
        state_label = "⚪ STANDBY"
        label_color = "var(--text-muted)"

        if mic_state == "Listening":
            state_tag = "listening-wave"
            state_label = "🟢 RECORDING // MIC ON"
            label_color = "#10B981"
        elif mic_state == "Processing":
            state_tag = "processing-wave"
            state_label = "🟡 COGNITIVE SYNAPSE"
            label_color = "#F59E0B"
        elif mic_state == "Speaking":
            state_tag = "speaking-wave"
            state_label = "🔴 DE-CODING SPEECH"
            label_color = "#EC4899"

        voice_hud = textwrap.dedent(f"""
            <div class="voice-assistant-hud" style="position:relative; width:100%; font-family:var(--font-mono);">
                <div class="corner-bracket tl" style="width:8px; height:8px; border-width:1.5px 0 0 1.5px;"></div>
                <div class="corner-bracket tr" style="width:8px; height:8px; border-width:1.5px 1.5px 0 0;"></div>
                <div class="corner-bracket bl" style="width:8px; height:8px; border-width:0 0 1.5px 1.5px;"></div>
                <div class="corner-bracket br" style="width:8px; height:8px; border-width:0 1.5px 1.5px 0;"></div>

                <p class="panel-title" style="margin-bottom:10px; letter-spacing:2px;">AUDIO INTERCEPT</p>

                <!-- Signal Status Badge -->
                <div style="font-family:var(--font-mono); font-size:0.6rem; color:var(--text-muted); text-align:center; margin-bottom:12px;">
                    COMMS CHANNEL STATE: <span style="color:{label_color}; font-weight:600; text-shadow:0 0 8px {label_color}44;">{state_label}</span>
                </div>

                <!-- Custom SVG Waveform visualizer -->
                <div class="mic-wave-glow" style="margin-bottom:15px; display:flex; justify-content:center; align-items:center; background:rgba(0,0,0,0.2); border:1px solid rgba(0,217,255,0.06); border-radius:6px; padding:6px 0;">
                    <svg width="180" height="40" viewBox="0 0 180 40" class="voice-waveform-svg" style="width:90%; overflow:visible;">
                        <path class="wave-line wave-back" d="M 0,20 Q 20,2 40,20 T 80,20 T 120,20 T 160,20 T 180,20" fill="none" stroke="rgba(123, 97, 255, 0.35)" stroke-width="1.5"/>
                        <path class="wave-line wave-middle" d="M 0,20 Q 15,10 30,20 T 60,20 T 90,20 T 120,20 T 150,20 T 180,20" fill="none" stroke="rgba(0, 217, 255, 0.25)" stroke-width="1"/>
                        <path class="wave-line wave-front" d="M 0,20 Q 25,38 50,20 T 100,20 T 150,20 T 180,20" fill="none" stroke="var(--neon-cyan)" stroke-width="2" style="filter:drop-shadow(0 0 3px var(--neon-cyan));"/>
                    </svg>
                </div>
            </div>

            <style>
                .voice-waveform-svg {{ width:100%; overflow:visible; }}
                .wave-line {{ stroke-linecap:round; }}
                .wave-front {{ animation: wave-slide 1.8s linear infinite; transform-origin: center; }}
                .wave-middle {{ animation: wave-slide 2.8s linear infinite reverse; transform-origin: center; }}
                .wave-back {{ animation: wave-slide-reverse 3.8s linear infinite; transform-origin: center; }}

                @keyframes wave-slide {{
                    0% {{ transform: scaleY(1.0) rotate(0deg); }}
                    50% {{ transform: scaleY(1.5) rotate(0.3deg); }}
                    100% {{ transform: scaleY(1.0) rotate(0deg); }}
                }}
                @keyframes wave-slide-reverse {{
                    0% {{ transform: scaleY(1.0); }}
                    50% {{ transform: scaleY(0.6); }}
                    100% {{ transform: scaleY(1.0); }}
                }}

                /* State specific waveforms */
                .listening-wave .wave-front {{ animation-duration: 0.6s; }}
                .speaking-wave .wave-front {{ animation-duration: 0.22s; }}
                .processing-wave .wave-front {{ animation-duration: 1.2s; filter: hue-rotate(90deg); }}
            </style>
        """).strip()

        st.markdown(voice_hud, unsafe_allow_html=True)

        # Alt PTT execution
        ptt_disabled = mic_state in ("Listening", "Processing", "Speaking")

        # Renders the PTT trigger button
        if st.button(
            "⚡ INITIATE TRANSMISSION",
            use_container_width=True,
            key="ptt_voice_trigger_modular",
            disabled=ptt_disabled
        ):
            with st.spinner("🎤 Listening... Speak now!"):
                user_text, response = voice_manager.trigger_ptt()

            if response:
                if user_text:
                    st.session_state.messages.append({
                        "role": "user",
                        "content": f"🎤 {user_text}"
                    })
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })
                from modules.memory import save_memory
                save_memory(st.session_state.messages)
                voice_manager.tts_player.speak(response)

            st.session_state.active_view = "Chats"
            st.rerun()

        st.markdown(
            '<div style="font-size:0.58rem; color:var(--text-muted); text-align:center; '
            'font-family:\'Share Tech Mono\', monospace; margin-top:4px; letter-spacing:1px;">'
            'HOTKEY: ALT + SPACE</div>',
            unsafe_allow_html=True
        )
