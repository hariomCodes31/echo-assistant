import os
import tempfile
import speech_recognition as sr
from groq import Groq
from dotenv import load_dotenv

# Ensure .env is loaded reliably regardless of working directory
_ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
load_dotenv(dotenv_path=_ENV_PATH)

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def record_and_transcribe(
    device_index=None,
    timeout=8,
    phrase_time_limit=12,
    calibration_duration=0.25,
    pause_threshold=0.8
):
    """
    Record audio from the microphone and transcribe it using Groq Whisper API.
    
    Fixes applied:
    1. Dynamic ambient noise calibration (0.25s) adapts to any room noise or mic gain.
    2. Dynamic energy threshold enabled so quiet voices and loud rooms are both handled.
    3. Safe threshold clamping [120, 1500] prevents oversensitivity and deafness.
    4. Pause threshold set to 0.8s so natural speech pauses between words don't cut off audio prematurely.
    5. Fallback transcription model (whisper-large-v3-turbo) if primary model experiences latency.
    """
    recognizer = sr.Recognizer()

    # Dynamic threshold configuration:
    # Allows the recognizer to continuously adapt to changing background noise levels
    recognizer.dynamic_energy_threshold = True
    recognizer.dynamic_energy_adjustment_damping = 0.15
    recognizer.dynamic_energy_ratio = 1.5

    # Pause threshold: 0.8 seconds of silence to consider the phrase complete
    recognizer.pause_threshold = max(0.5, pause_threshold)
    recognizer.phrase_threshold = 0.25  # Minimum speaking duration to consider it a phrase
    recognizer.non_speaking_duration = max(0.2, recognizer.pause_threshold - 0.3)

    # Select the microphone source
    mic = sr.Microphone(device_index=device_index)

    with mic as source:
        # Calibrate for ambient background noise to establish baseline noise floor
        if calibration_duration > 0:
            try:
                recognizer.adjust_for_ambient_noise(source, duration=calibration_duration)
            except Exception:
                pass

        # Clamp energy threshold to safe operational bounds
        recognizer.energy_threshold = max(120, min(recognizer.energy_threshold, 1500))

        # Listen for user speech
        audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

    # Retrieve audio as standard 16-bit PCM WAV bytes
    wav_data = audio.get_wav_data()

    # Write to a guaranteed-writable system temporary file
    temp_fd, temp_filename = tempfile.mkstemp(suffix=".wav", prefix="echo_voice_")
    os.close(temp_fd)

    with open(temp_filename, "wb") as f:
        f.write(wav_data)

    try:
        # Primary attempt: whisper-large-v3
        with open(temp_filename, "rb") as audio_file:
            try:
                transcription = client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-large-v3",
                    prompt="ECHO X voice assistant command transcription. Clear and accurate English words.",
                    temperature=0.0,
                    response_format="text"
                )
            except Exception:
                # Fallback to turbo model if primary has issues
                audio_file.seek(0)
                transcription = client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-large-v3-turbo",
                    prompt="ECHO X voice assistant command transcription.",
                    temperature=0.0,
                    response_format="text"
                )

        if isinstance(transcription, str):
            text = transcription.strip()
        else:
            text = transcription.text.strip() if hasattr(transcription, "text") else ""

        # Filter out common Whisper hallucination artifacts on quiet audio
        hallucinations = {"thank you.", "thank you", "thanks for watching.", "thanks for watching", ".", "you"}
        if text.lower() in hallucinations:
            return ""

        return text

    finally:
        # Always clean up the temporary recording file
        if os.path.exists(temp_filename):
            try:
                os.remove(temp_filename)
            except Exception:
                pass