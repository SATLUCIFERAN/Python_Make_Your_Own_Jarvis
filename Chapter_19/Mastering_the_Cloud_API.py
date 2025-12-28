import time
import subprocess
import pyttsx3 
import speech_recognition as sr
import webbrowser

import os
from google.cloud import speech 
from google.api_core import exceptions as gce_exceptions 

# -------------------------------------------------------------
## 1. Configuration Settings
# -------------------------------------------------------------

# --- Language Configuration ---
# Set the default recognition language using BCP-47 codes (e.g., "en-US", "es-ES", "fr-FR")

DEFAULT_LANGUAGE = "en-US"
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
    subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) 
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
    print(f"Jarvis ERROR: Could not initialize Google Cloud Speech Client.Check credentials and environment variables. Error: {e}")


def recognize_with_cloud_api(audio_data, language_code):    
    if cloud_client is None or audio_data is None:
        return ""
    
    try:        
        raw_bytes = audio_data.get_raw_data(convert_rate=TARGET_SAMPLE_RATE, 
                                            convert_width=2)
    except Exception as e:
        print(f"Jarvis: Failed to convert audio data for Cloud API: {e}")
        return ""

    audio = speech.RecognitionAudio(content=raw_bytes)
    
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16, 
        sample_rate_hertz=TARGET_SAMPLE_RATE, 
        language_code=language_code,
        enable_automatic_punctuation=True
    )

    try:        
        response = cloud_client.recognize(config=config, audio=audio)        
        if response.results:
            text = response.results[0].alternatives[0].transcript
            print(f"User Command (Dedicated Cloud API) [{language_code}]: {text}")
            return text    
    except gce_exceptions.GoogleAPICallError as api_e:        
        print(f"Jarvis: Dedicated Cloud API failed during transcription. Reason:\
              {type(api_e).__name__} (Code: {api_e.code}). Details: {api_e.message}")
        return ""
    except Exception as e:
        print(f"Jarvis: Dedicated Cloud API failed during transcription (Non-API Error):\
              {e}")
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
        # NOTE: voice_name is passed in from main() when jarvis_speak is called in a real implementation
        r.adjust_for_ambient_noise(source, duration=1.0)
        try:
            audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            return audio
        except sr.WaitTimeoutError:
            print("Jarvis: Listening timed out (no phrase detected).")
            return None


def convert_to_text(audio_data, voice_name=None, language_code=DEFAULT_LANGUAGE):
    
    if audio_data is None:
        return ""
    text = ""
    
    # 1. PRIMARY ATTEMPT: FREE GOOGLE WRAPPER (Tier 1)    
    try:        
        text = r.recognize_google(audio_data, language=language_code)
        print(f"User Command (Online/High-Accuracy) [{language_code}]: {text}")
        return text    
    except (sr.UnknownValueError, sr.RequestError):
        print("Jarvis: Primary online recognition failed. Attempting advanced mode...")
        
        # 2. SECONDARY ATTEMPT: DEDICATED GOOGLE CLOUD API (Tier 2)
        if cloud_client:
            print("Jarvis: Attempting dedicated Google Cloud API...")            
            text = recognize_with_cloud_api(audio_data, language_code)
            if text:
                return text
            else:
                print("Jarvis: Dedicated Cloud API failed. Falling back to local mode...")

        # 3. FINAL FALLBACK: OFFLINE LOCAL SPHINX STT (Tier 3)
        try:            
            text = r.recognize_sphinx(audio_data, language=language_code[:2]) 
            print(f"User Command (Offline/Local) [{language_code[:2]}]: {text}")
            return text

        except sr.UnknownValueError:
            jarvis_speak("Offline mode failed. Please speak clearly.", voice_name)
            return ""
        except sr.RequestError as sphinx_e:            
            print(f"Jarvis ERROR: PocketSphinx failed (Data Missing). Details: {sphinx_e}")
            jarvis_speak("Offline recognition data is missing. Please check the PocketSphinx installation.", voice_name)
            return ""
    
    except sr.UnknownValueError:        
        jarvis_speak("Online recognition failed. I couldn't understand the audio.", voice_name)
        return ""
    
    


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

# SET YOUR DESIRED LANGUAGE HERE (Change this to switch Jarvis's recognition language)

CURRENT_LANGUAGE = "en-US" 

def main():
    voice_name = set_jarvis_voice("David")
    jarvis_speak("System check complete. Jarvis is now ready.", voice_name)
    
    while True:
        # 1. Listening: Wait for the user to speak
        audio = jarvis_listen(timeout=5, phrase_time_limit=8) 
        
        # 2. Transcription: Use the 3-Tier Resiliency Chain
        command = convert_to_text(audio, voice_name, language_code=CURRENT_LANGUAGE)
        
        # 3. Command Parsing: Process the command (if one was successfully transcribed)
        if command:
            # Check for exit command (Case-insensitive)
            if "exit" in command.lower() or "shutdown" in command.lower():
                break 
            
            # Execute the command (in this case, just a web search)
            execute_web_search(command, voice_name)
            
    jarvis_speak("System shutting down. Goodbye.", voice_name)

if __name__ == "__main__":
    # WARNING: You must install PyAudio, pocketsphinx, AND google-cloud-speech
    main()