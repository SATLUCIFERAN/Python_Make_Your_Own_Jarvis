import time
import subprocess
import pyttsx3 
import speech_recognition as sr
import webbrowser

import os
from google.cloud import speech 
from google.api_core import exceptions as gce_exceptions 
# -------------------------------------------------------------
## 0. NEW: TextBlob Import for NLP
# -------------------------------------------------------------
from textblob import TextBlob 

# -------------------------------------------------------------
## 1. Configuration Settings
# -------------------------------------------------------------

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
    print(f"Jarvis ERROR: Could not initialize Google Cloud Speech Client. Check credentials and environment variables. Error: {e}")

# ... (recognize_with_cloud_api function remains unchanged) ...
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
        print(f"Jarvis: Dedicated Cloud API failed during transcription. Reason: {type(api_e).__name__} (Code: {api_e.code}). Details: {api_e.message}")
        return ""
    except Exception as e:
        print(f"Jarvis: Dedicated Cloud API failed during transcription (Non-API Error): {e}")
        return ""
    return ""

# -------------------------------------------------------------
## 4. Speech-to-Text (STT) Core Functions
# -------------------------------------------------------------

r = sr.Recognizer() 
r.energy_threshold = 400 

# ... (jarvis_listen and convert_to_text functions remain unchanged) ...
def jarvis_listen(timeout=5, phrase_time_limit=8):
    """Captures audio from the system's microphone."""
    with sr.Microphone() as source:
        print("--- Jarvis is Listening ---")
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

# -------------------------------------------------------------
## 5. Basic Execution Function (Stays for Fallback)
# -------------------------------------------------------------
def execute_web_search(text, voice_name):
    """Opens the user's default browser to a Google search query."""
    if text:
        search_url = f"https://www.google.com/search?q={text}"
        print(f"Jarvis: Executing search for '{text}'...")
        webbrowser.open(search_url)
        jarvis_speak(f"Search complete for {text}.", voice_name)


# -------------------------------------------------------------
## 6. Implementation of execute_youtube_search
# ------------------------------------------------------------- 
      
def execute_youtube_search(text, voice_name):
    """Opens the user's default browser to a YouTube search query."""
    if text: 
        search_url = f"https://www.youtube.com/results?search_query={text}"
        print(f"Jarvis: Executing YouTube search for '{text}'...")
        webbrowser.open(search_url)
        jarvis_speak(f"Video search complete for {text}.", voice_name)


# -------------------------------------------------------------
## 7. NEW: Intelligent Command Processor (SECTION 2.4 - FINAL SOLUTION)
# -------------------------------------------------------------

def parse_command_for_intent(command, voice_name): 

    blob = TextBlob(command)
    command_lower = command.lower()

    # Define the exclusion list globally for both steps 1 and 2
    EXCLUSION_WORDS = ["jarvis", "search", "result", "terrible", "execute", "that", "was", "a", "an", "the", "for", "i", "need", "to", "watch"]

    # 1. Extract and Filter Key Phrases (Standard TextBlob Noun Phrases)
    key_phrases_raw = [str(p).lower() for p in blob.noun_phrases] 
    
    # Filter out phrases that contain exclusion words (Fixes Bug 3: Excluding 'search')
    # This prevents command words from polluting the initial search_query if TextBlob captures them.
    key_phrases = []
    for phrase in key_phrases_raw:
        # Check if the phrase itself is a single exclusion word, or if it contains the full exclusion phrase (like 'jarvis')
        if not any(word in phrase.split() for word in EXCLUSION_WORDS if len(word)>3):
            key_phrases.append(phrase)

    # Start with the standard, filtered output
    search_query = " ".join(key_phrases)

    # 2. SMART QUERY GENERATION (Fixes Bug 2: Missing 'best')
    # If the standard noun phrase extraction is incomplete (less than 3 words) 
    # and the command is long, we use POS tagging as a fallback to capture adjectives.
    if len(search_query.split()) < 3 and len(command_lower.split()) > 4:
            
        tokens_and_tags = blob.tags
        smart_query_tokens = []

        for i, (token, tag) in enumerate(tokens_and_tags):
            # If a token is an Adjective (JJ) or Noun (NN, NNS, NNP, NNPS)
            if tag.startswith('JJ') or tag.startswith('NN'):
                # Add the token to the smart query list
                smart_query_tokens.append(token.lower())

        # Filter out command-related filler words, keeping actual subjects
        # This re-filters based on individual tokens, which is safer after POS tagging.
        smart_query_tokens = [t for t in smart_query_tokens if t not in EXCLUSION_WORDS] 
                
        # If the POS tags provide a better, longer subject, use it
        if len(smart_query_tokens) > len(search_query.split()):
            search_query = " ".join(smart_query_tokens)

    # 3. Check Sentiment
    sentiment_score = blob.sentiment.polarity 
    if sentiment_score < -0.3:
        jarvis_speak("I apologize for any issue. I will try to find a better result for you.", 
                      voice_name)

    # 4. Intent Routing
    if any(k in command_lower for k in ["video", "youtube", "watch"]): 
        if search_query:
            jarvis_speak(f"Routing to YouTube. Searching for: {search_query}.", voice_name)
            execute_youtube_search(search_query, voice_name) 
            return

    elif search_query:
    # IMPORTANT: This now uses the robust, smart search_query!
        jarvis_speak(f"Searching web for: {search_query}.", voice_name)
        execute_web_search(search_query, voice_name)
    else:
        jarvis_speak("Command acknowledged, but no specific action or target found.", 
    voice_name)
            
# -------------------------------------------------------------
## 8. Main Execution Flow (The Final Update)
# -------------------------------------------------------------

CURRENT_LANGUAGE = "en-US" 

def main():
    voice_name = set_jarvis_voice("David")
    jarvis_speak("System check complete. Jarvis is now ready.", voice_name)
    
    while True: 
        audio = jarvis_listen(timeout=5, phrase_time_limit=8) 
        command = convert_to_text(audio, voice_name, language_code=CURRENT_LANGUAGE) 
        if command: 
            if "exit" in command.lower() or "shutdown" in command.lower():
                break 
            parse_command_for_intent(command, voice_name) 

    jarvis_speak("System shutting down. Goodbye.", voice_name)

if __name__ == "__main__":
    # WARNING: You must install PyAudio, pocketsphinx, google-cloud-speech AND textblob
    main()