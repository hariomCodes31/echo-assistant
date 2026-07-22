import os
import time
import subprocess
import threading
import speech_recognition as sr
from groq import Groq
from dotenv import load_dotenv

# Import routing and memory functions
from modules.router import execute
from modules.memory import load_memory, save_memory
from modules.voice import record_and_transcribe

# Load env variables
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


class TTSPlayer:
    """
    Asynchronous Text-to-Speech player using native Windows PowerShell System.Speech.
    Runs speech processes in the background to prevent blocking the UI,
    and supports immediate subprocess termination for instant interruption.
    """
    def __init__(self):
        self.process = None
        self.volume = 100  # 0 to 100
        self.rate = 0  # -10 to 10
        self.voice_id = None
        self.active_speaking = False

    def set_settings(self, volume, rate, voice_id):
        self.volume = int(volume * 100)
        # Convert pyttsx3 range (100-300, default 200) to System.Speech range (-10 to 10, default 0)
        self.rate = int((rate - 200) / 10)
        self.voice_id = voice_id

    def speak(self, text):
        self.stop()
        if not text:
            return

        self.active_speaking = True

        # Clean text for PowerShell execution
        clean_text = text.replace("'", "''").replace('"', '""')
        # Remove common emoji/unicode symbols that cause encoding issues in PowerShell
        for ch in ["❌", "✅", "🤖", "📂", "📸", "⚪", "🟢", "🟡", "🔴", "🎤", "🔊",
                   "💬", "🖼️", "🎙️", "🖥️", "🌐", "🎵", "🌤", "⚙️", "🗑️"]:
            clean_text = clean_text.replace(ch, "")

        # Build PowerShell System.Speech script
        ps_script = "Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer;"
        ps_script += f"$s.Volume = {self.volume};"
        ps_script += f"$s.Rate = {self.rate};"
        if self.voice_id:
            ps_script += f"try {{ $s.SelectVoice('{self.voice_id}') }} catch {{}};"
        ps_script += f"$s.Speak('{clean_text}');"

        try:
            # Spawn PowerShell asynchronously
            self.process = subprocess.Popen(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            # Start a thread to monitor when speaking completes
            threading.Thread(target=self._monitor_speech, daemon=True).start()
        except Exception:
            self.active_speaking = False

    def stop(self):
        if self.process and self.process.poll() is None:
            try:
                self.process.kill()
            except Exception:
                pass
        self.active_speaking = False

    def _monitor_speech(self):
        if self.process:
            self.process.wait()
            self.active_speaking = False


class VoiceManager:
    """
    Manages Speech-to-Text, Natural Language Understanding,
    interruption commands, and continuous loop routing.
    """
    def __init__(self):
        self.tts_player = TTSPlayer()

        # UI/State Settings
        self.mic_index = None
        self.mode = "Push To Talk"  # Push To Talk, Continuous Listening, Wake Word Only
        self.enabled = False
        self.mic_state = "Idle"  # Listening, Processing, Speaking, Idle
        self.last_action = None
        self.interrupted = False

        # Background listener thread (only for continuous/wake word modes)
        self._listener_thread = threading.Thread(target=self._listening_loop, daemon=True)
        self._listener_thread.start()

    def update_settings(self, volume, rate, voice_id, mode, enabled, mic_index):
        self.tts_player.set_settings(volume, rate, voice_id)
        self.mode = mode
        self.enabled = enabled
        self.mic_index = mic_index

    def resolve_voice_intent(self, raw_speech):
        """
        Uses Groq LLM for Natural Language Understanding (NLU).
        Translates spoken queries into standard ECHO X commands and resolves pronouns.
        """
        system_prompt = f"""
You are the Natural Language Understanding (NLU) component of the ECHO X AI desktop assistant.
Your task is to map the user's spoken input to one of the exact system command formats listed below.

Standard Command Formats:
- open google
- open youtube
- open github
- search <query>
- play <song name>
- take screenshot
- weather in <city>
- analyze screenshot
- describe image
- read text
- what is in this image
- how many people
- what objects are there
- what color is the shirt
- analyze <filepath>
- describe <filepath>
- close chrome
- close spotify
- close vs code

PRONOUN RESOLUTION & CONTEXT:
If the user's command contains pronouns (like 'it', 'that', 'close it', 'open it') referring to the previous action, resolve it using the context provided below:
Context (Last Action): {self.last_action or "None"}

Examples and Browser mappings:
- Browser-based commands (open youtube, open google, open github, search <query>) all run inside Google Chrome. Thus, if the Last Action is any of these, and the user says "Close it" or "Close that", map it to "close chrome".
- If Last Action is "open spotify" and user says "Close it", return "close spotify".
- If Last Action is "open vscode" and user says "Close it", return "close vscode".
- If user says "Open VS Code", return "open vs code".
- If user says "Describe this image please", return "describe image".

RULES:
1. If the input maps to a system command, return ONLY that command string. Do not add any markdown, punctuation, prefix, or extra words.
2. If the input is conversational (e.g. "hello", "how are you", "what is your name"), return it exactly as-is.

Return ONLY the final translated command string.
"""
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": raw_speech}
                ],
                temperature=0.0,
                max_tokens=64
            )
            return response.choices[0].message.content.strip()
        except Exception:
            return raw_speech

    def process_voice_input(self, raw_text):
        """
        Processes a single transcribed voice string: NLU mapping -> routing -> execution.
        Returns (resolved_command, response_text) so the caller can update the UI and speak.
        """
        if not raw_text:
            return None, None

        # Check for immediate interruptions first
        clean_text = raw_text.lower().strip().strip("?.!,")
        interrupt_words = ["stop", "sop", "cancel", "quiet", "silence", "shh", "shush", "hush"]
        if clean_text in interrupt_words or any(w in clean_text.split() for w in interrupt_words):
            self.tts_player.stop()
            self.interrupted = True
            return raw_text, None

        self.mic_state = "Processing"

        # NLU intent resolution
        resolved_cmd = self.resolve_voice_intent(raw_text)

        # Route to execute()
        result = execute(resolved_cmd)

        if result:
            # Update last action if execution succeeded
            if not result.startswith("❌") and not result.startswith("⚠️"):
                self.last_action = resolved_cmd

            # Save history to memory.json
            self._save_to_chat_history(raw_text, result)
            return raw_text, result
        else:
            # Fallback to chat completion if not a system command
            from ai import ask_ai
            response = ask_ai(resolved_cmd)
            self._save_to_chat_history(raw_text, response)
            return raw_text, response

    def trigger_ptt(self):
        """
        Processes a single voice prompt via Push To Talk.
        Returns (user_text, response_text) for the caller to display and speak.
        """
        self.mic_state = "Listening"
        try:
            # Increase listening timeout to 7 seconds for a wider user response window
            transcription = record_and_transcribe(
                device_index=self.mic_index,
                timeout=7,
                phrase_time_limit=8,
                calibration_duration=0.0,
                pause_threshold=0.4
            )
            if transcription:
                return self.process_voice_input(transcription)
            else:
                self.mic_state = "Idle"
                msg = "I couldn't hear anything. Please try speaking again."
                return None, msg
        except sr.WaitTimeoutError:
            self.mic_state = "Idle"
            msg = "Listening timed out. No speech was detected. Please verify your selected microphone is active."
            return None, msg
        except Exception as e:
            self.mic_state = "Idle"
            msg = f"Error capturing speech: {str(e)}"
            return None, msg
        finally:
            self.mic_state = "Idle"

    def _listening_loop(self):
        """
        Continuous listening loop supporting Continuous Listening and Wake Word modes.
        """
        while True:
            if not self.enabled or self.mode == "Push To Talk":
                self.mic_state = "Idle"
                time.sleep(0.5)
                continue

            # Display correct visual mic state on the sidebar
            if self.tts_player.active_speaking:
                self.mic_state = "Speaking"
            else:
                self.mic_state = "Listening"

            try:
                # Continuous listener uses highly responsive parameters
                # phrase_time_limit is raised to 8 seconds to prevent cutting off longer commands
                transcription = record_and_transcribe(
                    device_index=self.mic_index,
                    timeout=2,
                    phrase_time_limit=8,
                    calibration_duration=0.0,
                    pause_threshold=0.4
                )

                if not transcription:
                    continue

                # Strip punctuation for matching keywords
                clean_txt = transcription.lower().replace(",", "").replace(".", "").replace("?", "").replace("!", "").strip()
                words = clean_txt.split()
                interrupt_words = ["stop", "sop", "cancel", "quiet", "silence", "shh", "shush", "hush"]

                # 1. Voice Interruption Check (Always checked first, even when assistant is speaking)
                if clean_txt in interrupt_words or any(w in words for w in interrupt_words):
                    self.tts_player.stop()
                    continue

                # 2. Skip processing commands if assistant is speaking to avoid voice feedback looping
                if self.tts_player.active_speaking:
                    continue

                # 3. Process commands based on mode
                if self.mode == "Wake Word Only":
                    if "echo" in words:
                        try:
                            echo_idx = words.index("echo")
                            cmd_words = words[echo_idx + 1:]
                            if cmd_words:
                                command_str = " ".join(cmd_words)
                                _, response = self.process_voice_input(command_str)
                                if response:
                                    self.mic_state = "Speaking"
                                    self.tts_player.speak(response)
                            else:
                                # Wake word only spoke, prompt the user
                                self.tts_player.speak("Yes, I am listening.")
                        except ValueError:
                            pass
                else:
                    # Continuous Listening mode: process everything transcribed
                    _, response = self.process_voice_input(transcription)
                    if response:
                        self.mic_state = "Speaking"
                        self.tts_player.speak(response)

            except sr.WaitTimeoutError:
                # Normal silence timeout in continuous mode; keep listening
                continue
            except Exception as e:
                self.mic_state = "Idle"
                print(f"[ECHO X Continuous Listener Error]: {e}")
                time.sleep(1.0)  # Short recovery delay before retrying

    def _save_to_chat_history(self, user_text, assistant_text):
        """Helper to sync voice conversations with memory.json."""
        try:
            messages = load_memory()
            messages.append({"role": "user", "content": f"[Voice Input] {user_text}"})
            messages.append({"role": "assistant", "content": assistant_text})
            save_memory(messages)
        except Exception:
            pass


# Global Voice Manager instance — created once per Python process lifetime
# Uses a module-level guard so it survives Streamlit reruns within the same worker process
_voice_manager_instance = None

def _get_voice_manager():
    global _voice_manager_instance
    if _voice_manager_instance is None:
        _voice_manager_instance = VoiceManager()
    return _voice_manager_instance


voice_manager = _get_voice_manager()
