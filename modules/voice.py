import os
import speech_recognition as sr
from groq import Groq
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def record_and_transcribe(device_index=None, timeout=5, phrase_time_limit=10, calibration_duration=0.0, pause_threshold=0.4):
    """
    Record audio from the microphone and transcribe it using the Groq Whisper API.
    Supports selecting microphone device_index.
    
    Uses a highly sensitive fixed energy threshold of 100 to capture voice inputs
    reliably under all noise environments without self-desensitization.
    """
    recognizer = sr.Recognizer()
    
    # Configure speech recognition settings for high responsiveness
    recognizer.energy_threshold = 100
    recognizer.dynamic_energy_threshold = False
    
    # Set the pause threshold to a lower value for much faster responsiveness after speaking
    recognizer.pause_threshold = pause_threshold
    # Ensure non_speaking_duration is less than or equal to pause_threshold to pass the library's internal assertion check
    recognizer.non_speaking_duration = max(0.1, pause_threshold - 0.1)
    
    # Select the microphone source
    mic = sr.Microphone(device_index=device_index)
    
    with mic as source:
        # Calibrate for background noise if requested (default is 0.0 to start listening immediately)
        if calibration_duration > 0:
            recognizer.adjust_for_ambient_noise(source, duration=calibration_duration)
            
        # Listen for user audio
        audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        
    # Retrieve audio as standard WAV bytes
    wav_data = audio.get_wav_data()
    
    # Write to a temporary file
    temp_filename = "temp_voice_recording.wav"
    with open(temp_filename, "wb") as f:
        f.write(wav_data)
        
    try:
        # Send audio to Groq Whisper API for translation
        with open(temp_filename, "rb") as audio_file:
            translation = client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-large-v3",
                prompt="ECHO X command transcription. Convert spoken words to text clearly.",
                temperature=0.0
            )
        return translation.text.strip()
        
    finally:
        # Always clean up the temporary recording file
        if os.path.exists(temp_filename):
            try:
                os.remove(temp_filename)
            except Exception:
                pass