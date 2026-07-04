import streamlit as st
import textwrap
from modules.voice_manager import voice_manager

def render_voice_panel():
    """
    Renders the active Voice Assistant panel, containing
    the responsive soundwave animation and the Push To Talk button widget.
    """
    with st.container(border=True):
        # Get active microphone state to trigger specific styling tags
        mic_state = voice_manager.mic_state  # now plain strings: Idle, Listening, Processing, Speaking
        state_tag = "idle-wave"
        state_label = "⚪ Idle"
        if mic_state == "Listening":
            state_tag = "listening-wave"
            state_label = "🟢 Listening"
        elif mic_state == "Processing":
            state_tag = "processing-wave"
            state_label = "🟡 Processing"
        elif mic_state == "Speaking":
            state_tag = "speaking-wave"
            state_label = "🔴 Speaking"

        st.markdown(f'<div class="voice-tray-widget {state_tag}">', unsafe_allow_html=True)
        st.markdown('<p class="panel-title" style="margin-bottom:6px;">Voice Assistant</p>', unsafe_allow_html=True)
        st.markdown(
            f'<div style="font-size:0.72rem; color:#64748B; text-align:center; margin-bottom:8px; font-family:\'Share Tech Mono\', monospace;">'
            f'Status: <span style="color:#00D9FF;">{state_label}</span></div>',
            unsafe_allow_html=True
        )

        # Custom SVG Waveform visualizer container
        voice_svg_html = textwrap.dedent("""
            <div class="mic-wave-glow" style="margin-bottom:15px; display:flex; justify-content:center; align-items:center;">
                <svg width="180" height="40" viewBox="0 0 180 40" class="voice-waveform-svg">
                    <path class="wave-line wave-back" d="M 0,20 Q 20,5 40,20 T 80,20 T 120,20 T 160,20 T 180,20" fill="none" stroke="rgba(123, 97, 255, 0.4)" stroke-width="1.5"/>
                    <path class="wave-line wave-front" d="M 0,20 Q 25,35 50,20 T 100,20 T 150,20 T 180,20" fill="none" stroke="#00D9FF" stroke-width="2"/>
                </svg>
            </div>
            <style>
                .voice-waveform-svg {
                    width: 100%;
                    overflow: visible;
                }
                .wave-line {
                    stroke-linecap: round;
                }
                .wave-front {
                    animation: wave-slide 2s linear infinite;
                    transform-origin: center;
                }
                .wave-back {
                    animation: wave-slide-reverse 4s linear infinite;
                    transform-origin: center;
                }
                @keyframes wave-slide {
                    0% { transform: scaleY(1.0) rotate(0deg); }
                    50% { transform: scaleY(1.4) rotate(0.5deg); }
                    100% { transform: scaleY(1.0) rotate(0deg); }
                }
                @keyframes wave-slide-reverse {
                    0% { transform: scaleY(1.0); }
                    50% { transform: scaleY(0.7); }
                    100% { transform: scaleY(1.0); }
                }

                /* State specific wave responses */
                .listening-wave .wave-front { animation-duration: 0.6s; }
                .speaking-wave .wave-front { animation-duration: 0.2s; }
            </style>
        """).strip()

        st.markdown(voice_svg_html, unsafe_allow_html=True)

        # ----- PTT EXECUTION (runs synchronously here on button press) -----
        ptt_disabled = mic_state in ("Listening", "Processing", "Speaking")

        if st.button(
            "🎤 Push To Talk",
            use_container_width=True,
            key="ptt_voice_trigger_modular",
            disabled=ptt_disabled
        ):
            # Run PTT inline with spinner — blocks the UI for the listening window
            # which is correct: the user wants to speak NOW
            with st.spinner("🎤 Listening... Speak now!"):
                user_text, response = voice_manager.trigger_ptt()

            if response:
                # Append both turns to the chat session
                if user_text:
                    st.session_state.messages.append({
                        "role": "user",
                        "content": f"🎤 {user_text}"
                    })
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })
                # Save updated memory
                from modules.memory import save_memory
                save_memory(st.session_state.messages)

                # Speak the response asynchronously
                voice_manager.tts_player.speak(response)

            # Switch to Chats view so user sees the response
            st.session_state.active_view = "Chats"
            st.rerun()

        st.markdown(
            '<div style="font-size:0.6rem; color:#64748B; text-align:center; '
            'font-family:\'Share Tech Mono\', monospace; margin-top:2px;">( Alt + Space )</div>',
            unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)
