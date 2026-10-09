import streamlit as st
import subprocess
import speech_recognition as sr
from modules.voice_manager import voice_manager

def get_installed_voices():
    try:
        ps_cmd = "Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.GetInstalledVoices() | ForEach-Object { $_.VoiceInfo.Name }"
        res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True, check=True)
        output = res.stdout.strip()
        voices = [v.strip() for v in output.replace("\r\n", "\n").split("\n") if v.strip()]
        return voices if voices else ["Microsoft David Desktop", "Microsoft Zira Desktop"]
    except Exception:
        return ["Microsoft David Desktop", "Microsoft Zira Desktop"]

def get_input_microphones():
    """Returns list of genuine input audio devices (index, name)."""
    devices = []
    try:
        import pyaudio
        p = pyaudio.PyAudio()
        for i in range(p.get_device_count()):
            try:
                info = p.get_device_info_by_index(i)
                if info.get("maxInputChannels", 0) > 0:
                    raw_name = info.get("name", f"Microphone {i}").replace("\r", " ").replace("\n", " ").strip()
                    devices.append((i, raw_name))
            except Exception:
                pass
        p.terminate()
    except Exception:
        try:
            for i, name in enumerate(sr.Microphone.list_microphone_names()):
                devices.append((i, name.replace("\r", " ").replace("\n", " ").strip()))
        except Exception:
            pass
    return devices

def load_voice_settings_page():
    st.markdown('<p class="panel-title" style="font-size:1.5rem; color:#00D9FF; letter-spacing:2px; text-transform:uppercase;">🎙️ Voice Calibration Dashboard</p>', unsafe_allow_html=True)
    
    col_config, col_output = st.columns([5, 5])
    
    # Left column: Speech to Text config
    with col_config:
        with st.container(border=True):
            st.markdown('<p class="panel-title">Speech Input & Trigger Logic</p>', unsafe_allow_html=True)
            
            # Voice Mode Enabled
            is_enabled = st.toggle("Enable Continuous Microphone", value=voice_manager.enabled, help="When enabled, the assistant listens in the background for commands or the wake word.")
            
            # Trigger Mode
            mode_options = ["Push To Talk", "Continuous Listening", "Wake Word Only"]
            current_mode = voice_manager.mode
            selected_mode = st.radio("Voice Operation Mode", options=mode_options, index=mode_options.index(current_mode) if current_mode in mode_options else 0)
            
            # Microphone device dropdown - only genuine input devices
            input_devices = get_input_microphones()
            mic_options = ["Default System Microphone"] + [f"[{idx}] {name}" for idx, name in input_devices]
            
            # Match current mic selection
            current_mic = voice_manager.mic_index
            default_index = 0
            if current_mic is not None:
                for opt_idx, (d_idx, _) in enumerate(input_devices, start=1):
                    if d_idx == current_mic:
                        default_index = opt_idx
                        break
                
            selected_mic_str = st.selectbox("Active Audio Input Device", options=mic_options, index=default_index)
            
            if selected_mic_str == "Default System Microphone":
                selected_mic_index = None
            else:
                try:
                    selected_mic_index = int(selected_mic_str.split("]")[0].replace("[", ""))
                except Exception:
                    selected_mic_index = None
                    
            # Update background properties
            voice_manager.enabled = is_enabled
            voice_manager.mode = selected_mode
            voice_manager.mic_index = selected_mic_index

    # Right column: Speech synthesis config
    with col_output:
        with st.container(border=True):
            st.markdown('<p class="panel-title">Speech Synthesizer Output</p>', unsafe_allow_html=True)
            
            # Volume control (converting 0.0-1.0 from voice_manager to slide)
            current_vol = float(voice_manager.tts_player.volume) / 100.0
            selected_vol = st.slider("Speech Volume", min_value=0.0, max_value=1.0, value=current_vol, step=0.1)
            
            # Speed/Rate control
            current_rate = int((voice_manager.tts_player.rate * 10) + 200)
            selected_rate = st.slider("Speech Rate / Speed", min_value=100, max_value=300, value=current_rate, step=10)
            
            # Voice selection
            installed_voices = get_installed_voices()
            current_voice = voice_manager.tts_player.voice_id
            
            default_voice_idx = 0
            for i, v in enumerate(installed_voices):
                if current_voice and current_voice.lower() in v.lower():
                    default_voice_idx = i
                    break
                    
            selected_voice = st.selectbox("Synthesis Voice ID", options=installed_voices, index=default_voice_idx)
            
            # Apply changes
            voice_manager.update_settings(
                volume=selected_vol,
                rate=selected_rate,
                voice_id=selected_voice,
                mode=selected_mode,
                enabled=is_enabled,
                mic_index=selected_mic_index
            )
            
            st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
            
            # Test Voice
            test_phrase = st.text_input("Speech Testing Prompt", value="ECHO OS Voice synthesizers online and operational.")
            if st.button("🔊 Play Test Phrase", use_container_width=True):
                with st.spinner("Synthesizing..."):
                    voice_manager.tts_player.speak(test_phrase)
                    
    # Bottom information panel
    with st.container(border=True):
        st.markdown('<p class="panel-title">Current Voice Status</p>', unsafe_allow_html=True)
        col_s1, col_s2, col_s3 = st.columns(3)
        
        state_display_map = {
            "Idle": "⚪ Idle",
            "Listening": "🟢 Listening",
            "Processing": "🟡 Processing",
            "Speaking": "🔴 Speaking",
        }
        display_state = state_display_map.get(voice_manager.mic_state, voice_manager.mic_state)
        
        with col_s1:
            st.markdown(f"**Mic State:** `{display_state}`")
        with col_s2:
            st.markdown(f"**Trigger Mode:** `{voice_manager.mode}`")
        with col_s3:
            st.markdown(f"**Target System:** `System.Speech (PowerShell Core)`")
