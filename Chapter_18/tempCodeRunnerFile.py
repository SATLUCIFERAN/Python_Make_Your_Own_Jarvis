import time
import subprocess
import pyttsx3 
import speech_recognition as sr
import webbrowser
import os
from google.cloud import speech 

# -------------------------------------------------------------
## 1. Configuration Settings
# -------------------------------------------------------------

# --- Language Configuration ---
# Set the default recognition language using BCP-47 codes (e.g., "en-US", "es-ES", "fr-FR")
DEFAULT_LANGUAGE = "en-US" 

# --- Cloud API Standards ---
# Required sample rate for Google Cloud API for best results
TARGET_SAMPLE_RATE = 16000 

# -------------------------------------------------------------
## 2. Text-to-Speech (TTS) Functions
# -------------------------------------------------------------

engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 0.9)

def jarvis_speak(text, voice=None): 
    """Handles text-to-speech output using PowerShell (Windows-only)."""
    print(f"Jarvis Output: {text} [Spoken]")
    safe_text = text.replace("'", "''")
    cmd = [
        "powershell", "-NoProfile", "-Command", 
        f"Add-Type -AssemblyName System.Speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        f"$speak.Speak('{safe_text}')"
    ]
    # NOTE: This PowerShell command is Windows-only. macOS/Linux require alternatives.
    # To execute speech, uncomment the line below:
    # subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) 
    time.sleep(len(text) / 200) 

def set_jarvis_voice(user_voice="Zira"):
    """Returns a default voice name for the system to use."""
    return "Microsoft David Desktop - English (United States)"

# -------------------------------------------------------------
## 3. Dedicated Google Cloud Client Setup (Tier 2)
# -------------------------------------------------------------

cloud_client = None
try:
    # Attempts to initialize the client using GOOGLE_APPLICATION_CREDENTIALS
    cloud_client = speech.SpeechClient()
    print("Jarvis: Dedicated Google Cloud client initialized successfully.")
except Exception as e:
    print(f"Jarvis ERROR: Could not initialize Google Cloud Speech Client. Check credentials and environment variables. Error: {e}")


def recognize_with_cloud_api(audio_data, language_code):
    """
    Transcribes AudioData using the dedicated Google Cloud API (Tier 2 Fallback).
    Ensures proper 16-bit, 16kHz encoding (LINEAR16).
    """
    if cloud_client is None or audio_data is None:
        return ""
    
    try:
        # CRITICAL: Convert audio bytes to the required 16 kHz, 16-bit format
        raw_bytes = audio_data.get_raw_data(convert_rate=TARGET_SAMPLE_RATE, convert_width=2)
    except Exception as e:
        print(f"Jarvis: Failed to convert audio data for Cloud API: {e}")
        return ""

    audio = speech.RecognitionAudio(content=raw_bytes)
    
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16, 
        sample_rate_hertz=TARGET_SAMPLE_RATE, # Must match the converted data
        language_code=language_code,
        enable_automatic_punctuation=True
    )
    try:
        # NOTE: recognize() is for short audio (~60s). Use long_running_recognize() for longer files.
        response = cloud_client.recognize(config=config, audio=audio)
        
        if response.results:
            text = response.results[0].alternatives[0].transcript
            print(f"User Command (Dedicated Cloud API) [{language_code}]: {text}")
            return text
    except Exception as e:
        print(f"Jarvis: Dedicated Cloud API failed during transcription: {e}")
        return ""
    return ""

# -------------------------------------------------------------
## 4. Speech-to-Text (STT) Core Functions
# -------------------------------------------------------------

r = sr.Recognizer() 
r.energy_threshold = 400 

def jarvis_listen(timeout=5, phrase_time_limit=8):
    """Captures audio from the system's microphone."""
    with sr.Microphone() as source:
        print("--- Jarvis is Listening ---")
        # NOTE: Using placeholder voice_name, ensure set_jarvis_voice is called in main
        r.adjust_for_ambient_noise(source, duration=1.0)
        try:
            audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            return audio
        except sr.WaitTimeoutError:
            print("Jarvis: Listening timed out (no phrase detected).")
            return None


def convert_to_text(audio_data, voice_name=None, language_code=DEFAULT_LANGUAGE):
    """
    3-Tier Resiliency: Free Google -> Dedicated Cloud -> Offline Sphinx.
    Uses the specified language_code for online tiers.
    """
    if audio_data is None:
        return ""
    text = ""
    
    # 1. PRIMARY ATTEMPT: FREE GOOGLE WRAPPER (Tier 1)
    try:
        # Pass language_code to the wrapper
        text = r.recognize_google(audio_data, language=language_code)
        print(f"User Command (Online/High-Accuracy) [{language_code}]: {text}")
        return text
    
    except (sr.UnknownValueError, sr.RequestError):
        print("Jarvis: Primary online recognition failed. Attempting advanced mode...")
        
        # 2. SECONDARY ATTEMPT: DEDICATED GOOGLE CLOUD API (Tier 2)
        if cloud_client:
            print("Jarvis: Attempting dedicated Google Cloud API...")
            # Pass language_code to the Cloud function
            text = recognize_with_cloud_api(audio_data, language_code)
            if text:
                return text
            else:
                print("Jarvis: Dedicated Cloud API failed. Falling back to local mode...")

        # 3. FINAL FALLBACK: OFFLINE LOCAL SPHINX STT (Tier 3)
        try:
            # Sphinx uses ISO 639-1 format (e.g., 'en', 'es'). We use the first two characters.
            text = r.recognize_sphinx(audio_data, language=language_code[:2]) 
            print(f"User Command (Offline/Local) [{language_code[:2]}]: {text}")
            return text

        except sr.UnknownValueError:
            jarvis_speak("Offline mode failed. Please speak clearly.", voice_name)
            return ""
    
    except sr.UnknownValueError:
        # This handles the case where the audio quality was too poor for any online recognizer
        jarvis_speak("Online recognition failed. I couldn't understand the audio.", voice_name)
        return ""
    
    return text


def execute_web_search(text, voice_name):
    """Opens the user's default browser to a Google search query."""
    if text:
        search_url = f"https://www.google.com/search?q={text}"
        print(f"Jarvis: Executing search for '{text}'...")
        webbrowser.open(search_url)
        jarvis_speak(f"Search complete for {text}.", voice_name)

# -------------------------------------------------------------
## 5. Main Execution Flow
# -------------------------------------------------------------

voice_name = set_jarvis_voice("David")

# SET YOUR DESIRED LANGUAGE HERE (Change this to switch Jarvis's recognition language)
CURRENT_LANGUAGE = "en-US" 

def main():
    
    jarvis_speak("System check complete. Jarvis is now ready.", voice_name)
    
    while True:
        audio = jarvis_listen(timeout=5, phrase_time_limit=8) 
        # Pass the chosen language code to convert_to_text
        command = convert_to_text(audio, voice_name, language_code=CURRENT_LANGUAGE)
        
        # Check for exit command (Case-insensitive)
        if command and "exit" in command.lower():
            break 
        
        # Execute the command
        if command:
            execute_web_search(command, voice_name)
            
    jarvis_speak("System shutting down. Goodbye.", voice_name)

if __name__ == "__main__":
    # WARNING: You must install PyAudio, pocketsphinx, AND google-cloud-speech
    main()