# CODE LOCATION: jarvis-assistant/main.py (FINAL VERSION WITH CLIPBOARD FALLBACK - INDENTATION FIXED)

import os
import pvporcupine
from pvrecorder import PvRecorder
import threading 
import speech_recognition as sr

import platform 
from pathlib import Path
from queue import Queue
import time
import traceback
import re 
try:
    import pyperclip # NEW: Import for clipboard access
except ImportError:
    # Set a fallback if the user hasn't installed the optional library
    print("Warning: pyperclip not installed. Install with 'pip install pyperclip' for clipboard integration.")
    pyperclip = None

# --- MODULAR SKILL IMPORTS ---
from skills.pdf_parser import pdf_parse      # Primary, fast parser (for clean PDFs)
from skills.pdf_ocr import image_ocr         # Secondary, dedicated OCR tool (for scanned PDFs)
from skills.yt_tools import yt_inspect, yt_summarize # NEW: YouTube skills

# --- CONDITIONAL IMPORTS ---
SYSTEM_OS = platform.system()
if SYSTEM_OS == "Windows":
    try:
        import win32com.client # Best for non-blocking speech on Windows
        print("TTS Backend: win32com (Windows)")
    except ImportError:
        print("FATAL ERROR: win32com.client not found. Install with 'pip install pywin32'")
        exit()
    # Global pyttsx3 variables are not used on Windows
    tts_engine_win = None
    engine_driver_name = 'sapi5'
    speech_queue = Queue() # Queue still used for flow control
else:
    import pyttsx3 # Best for reliability and cross-platform simplicity on Unix/Mac
    print(f"TTS Backend: pyttsx3 ({SYSTEM_OS})")
    # Global pyttsx3 variables
    tts_engine = None
    speech_queue = Queue()
    if SYSTEM_OS == "Darwin":
        engine_driver_name = 'nsss'
    else: # Linux
        engine_driver_name = 'espeak'

# --- 1. TTS INITIALIZATION (OS Specific) ---

def initialize_tts_global():
    global tts_engine, tts_engine_win

    if SYSTEM_OS == "Windows":
        try:
            # Initialize the SAPI.SpVoice client object once
            tts_engine_win = win32com.client.Dispatch("SAPI.SpVoice")
            tts_engine_win.Rate = 0 
            print("Windows TTS Client initialized. Rate set to 0 (Default).")
        except Exception as e:
            print(f"CRITICAL TTS FAILURE (win32com): {e}")
            tts_engine_win = None
    else:
        # macOS/Linux: Initialize pyttsx3 once to store properties
        try:
            tts_engine = pyttsx3.init(engine_driver_name)
            rate = tts_engine.getProperty('rate')
            tts_engine.setProperty('rate', rate)
            print("pyttsx3 Global Engine properties set to default rate.")
        except Exception as e:
            print(f"Jarvis TTS Error: Failed to initialize pyttsx3 engine. Error: {e}") 
            tts_engine = None

initialize_tts_global()


# --- 2. TTS WORKER THREAD (OS Specific Logic) ---

def _speak_pyttsx3(text):
    """(macOS/Linux) Non-blocking pyttsx3 disposable engine logic."""
    temp_engine = None
    try:
        # Re-initialize engine (disposable resource pattern)
        temp_engine = pyttsx3.init(engine_driver_name)
        temp_engine.setProperty('rate', tts_engine.getProperty('rate'))
        
        temp_engine.say(text)
        temp_engine.startLoop(False) 
        time.sleep(0.5) 
        
    except Exception as e:
        print(f"[TTS Worker Error - pyttsx3]: {e}")
        traceback.print_exc()
    finally:
        if temp_engine:
            try:
                temp_engine.stop() 
                del temp_engine
            except:
                pass

def _speak_win32com(text):
    """(Windows) Truly asynchronous win32com speak logic."""
    if tts_engine_win:
        try:
            tts_engine_win.Speak(text, 1) # SVSFlagsAsync = 1
            time.sleep(2) # CRITICAL FIX: Delay to allow response audio to finish
            
        except Exception as e:
            print(f"[TTS Worker Error - win32com]: {e}")
            traceback.print_exc()

def tts_worker():
    """Generic worker that delegates to the correct OS-specific speaker."""
    print("[TTS Worker] Started and waiting for speech...")
    while True:
        text = speech_queue.get()
        if text is None:
            break
        
        print(f"[TTS Worker] Received: {text[:50]}...")
        
        if SYSTEM_OS == "Windows":
            _speak_win32com(text)
        else:
            _speak_pyttsx3(text)
            
        print("[TTS Worker] Speech command sent!")
        speech_queue.task_done() # CRITICAL: Guarantees the main thread continues


def start_tts_worker():
    """Start the TTS worker thread."""
    if SYSTEM_OS == "Windows" and tts_engine_win or SYSTEM_OS != "Windows" and tts_engine:
        worker = threading.Thread(target=tts_worker, daemon=True)
        worker.start()
        time.sleep(0.2)
        print("TTS Worker Thread Started")


def jarvis_speak(text): 
    """Queue text for non-blocking speech."""
    print(f"\n[JARVIS]: {text}\n")
    is_engine_ready = (SYSTEM_OS == "Windows" and tts_engine_win) or (SYSTEM_OS != "Windows" and tts_engine)

    if is_engine_ready:
        print(f"[Main] Queuing: {text[:30]}... (Queue size: {speech_queue.qsize()})")
        speech_queue.put(text)
    else:      
        print(f"[JARVIS SPEAKS (Fallback)]: {text}")


# -------------------------------------------------------------
## Wake Word Engine Functions 
# -------------------------------------------------------------

ACCESS_KEY = os.environ.get("PICOVOICE_ACCESS_KEY")
WAKE_WORD = "jarvis" 

def wake_word_loop():

    if not ACCESS_KEY:
        print("Jarvis ERROR: PICOVOICE_ACCESS_KEY environment variable not set.")
        return None
    
    try:
        porcupine = pvporcupine.create(
            access_key=ACCESS_KEY,
            keywords=[WAKE_WORD]
        )

    except Exception as e:
        print(f"Jarvis ERROR: Failed to initialize Porcupine. Error: {e}")
        return None

    recorder = PvRecorder(
        frame_length=porcupine.frame_length,
        device_index=-1 
    )
    recorder.start()
    print(f"Listening passively for '{WAKE_WORD}'...")

    try:
        while True:      
            pcm = recorder.read()      
            keyword_index = porcupine.process(pcm)                           
            if keyword_index >= 0:
                print(f"Wake Word Detected: {WAKE_WORD.upper()}!")
                break 
    finally:                  
        porcupine.delete()         
    return recorder 


# -------------------------------------------------------------
## Main Execution (Live STT)
# -------------------------------------------------------------

def listen_for_command(recorder, recognizer):

    if not recorder:
        return None            
    recorder.stop()

    print("--- Waiting for speech to complete...")
    speech_queue.join() 
    time.sleep(0.3)    # Extra buffer for audio device cleanup

    with sr.Microphone() as source:
        print("--- JARVIS: Active Listening State. Speak Now... ---")
        recognizer.adjust_for_ambient_noise(source) 
        
        try:                           
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)                             
            command = recognizer.recognize_google(audio)
            print("---     JARVIS: Processing audio... ---")
            return command.lower()
            
        except sr.WaitTimeoutError:
            print("---     Timeout: No command heard. ---")
            return None
        except sr.UnknownValueError:
            print("---     Unknown Value: Could not understand audio. ---")
            return None
        except sr.RequestError as e:
            print(f"---    STT Error: Could not request results from Google; {e} ---")
            return None


# -------------------------------------------------------------
## NEW SKILL: Standard PDF Parsing (For Clean Text)
# -------------------------------------------------------------

def handle_pdf_parse(command, file_name="data/sample.pdf"):
    """Reads PDF using the fast, standard text parser (pdf_parse)."""
    file_path = Path(__file__).parent / file_name

    if not file_path.exists():
        jarvis_speak(f"Error: The document {file_path.name} was not found.")
        return False
    
    jarvis_speak(f"Parsing the clean document, {file_path.name}. Please wait.")

    clean_text = pdf_parse(str(file_path))

    if not clean_text or len(clean_text.strip()) < 50:
        jarvis_speak("Standard parser could not extract meaningful text. Try using the 'OCR' command.")
        return False

    jarvis_speak(f"Now reading the document. The document begins: {clean_text[:200]}...")

    print("\n--- FULL EXTRACTED PDF CONTENT (Parser) ---")
    print(clean_text)
    print("-----------------------------------")
    print(f"Total length: {len(clean_text)} characters.")

    return True

# -------------------------------------------------------------
## NEW SKILL: OCR Parsing (For Scanned Images)
# -------------------------------------------------------------

def handle_pdf_ocr(command, file_name="data/scanned_sample.png"):
    """Reads PDF using the slow, image-based OCR method (image_ocr)."""
    file_path = Path(__file__).parent / file_name

    if not file_path.exists():
        jarvis_speak(f"Error: The scanned document {file_path.name} was not found.")
        return False
    
    jarvis_speak(f"Starting OCR process on {file_path.name}. This may take a moment.")

    # Call the dedicated OCR function from skills/pdf_ocr.py
    ocr_text = image_ocr(str(file_path))

    if not ocr_text or len(ocr_text.strip()) < 50:
        jarvis_speak("OCR failed to extract meaningful text. Check your Tesseract/Poppler installation.")
        return False

    jarvis_speak(f"OCR successful. Reading document. It begins: {ocr_text[:200]}...")

    print("\n--- FULL EXTRACTED PDF CONTENT (OCR) ---")
    print(ocr_text)
    print("-----------------------------------")
    print(f"Total length: {len(ocr_text)} characters.")

    return True

# -------------------------------------------------------------
## NEW SKILL: YouTube Metadata (Fast Inspection)
# -------------------------------------------------------------

def handle_yt_inspect(command):
    """
    Extracts metadata from a YouTube URL found in the command text, 
    falling back to checking the system clipboard.
    """
    # 1. Attempt to find a YouTube URL in the spoken command
    url_match = re.search(r'https?://(?:www\.)?(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|v/))([\w-]{11})', command)
    full_url = None
    
    if url_match:
        full_url = url_match.group(0) # URL found in speech
    elif pyperclip:
        # 2. If no URL in command, check the clipboard
        try:
            clipboard_content = pyperclip.paste()
            # 3. Check if the clipboard content is a YouTube URL
            clipboard_match = re.search(r'https?://(?:www\.)?(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|v/))([\w-]{11})', clipboard_content)
            if clipboard_match:
                full_url = clipboard_match.group(0)
                jarvis_speak("Found a YouTube link on your clipboard. Proceeding with inspection.")
            else:
                print("LOGIC: Clipboard content was not a YouTube URL.")
        except Exception as e:
            # Clipboard read can fail if environment is headless
            print(f"Warning: Could not read clipboard. Error: {e}")

    if not full_url:
        # 4. If neither source has a valid URL
        jarvis_speak("Please copy a valid YouTube link to your clipboard and try again, or include the link in your command.")
        return False
        
    # --- Execution continues if full_url is found ---
    
    # Assuming yt_inspect is imported from skills.yt_tools
    jarvis_speak(f"Inspecting video. Please wait a moment.")
    
    metadata = yt_inspect(full_url)
    
    if not metadata:
        jarvis_speak("I could not retrieve metadata for that video. It might be private or geo-restricted.")
        return False
        
    response = (
        f"The video is titled: {metadata['title']}. "
        f"It is from the channel {metadata['channel']} and runs for {metadata['duration']}."
    )
    jarvis_speak(response)
    
    print("\n--- EXTRACTED YOUTUBE METADATA ---")
    print(metadata)
    print("-----------------------------------")
    
    return True

# -------------------------------------------------------------
## NEW SKILL: YouTube Transcript/Summary (Slower)
# -------------------------------------------------------------

def handle_yt_summarize(command, lang="en"):
    """
    Extracts the full transcript from a YouTube URL found in the command text,
    with clipboard fallback.
    """
    # 1. Attempt to find a YouTube URL in the spoken command
    url_match = re.search(r'https?://(?:www\.)?(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|v/))([\w-]{11})', command)
    full_url = None
    
    if url_match:
        full_url = url_match.group(0)
    elif pyperclip:
        # 2. If no URL in command, check the clipboard
        try:
            clipboard_content = pyperclip.paste()
            clipboard_match = re.search(r'https?://(?:www\.)?(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|v/))([\w-]{11})', clipboard_content)
            if clipboard_match:
                full_url = clipboard_match.group(0)
                jarvis_speak("Found a YouTube link on your clipboard.")
        except:
            pass # Ignore clipboard read errors

    if not full_url:
        jarvis_speak("Please copy a valid YouTube link to your clipboard and try again, or include the link in your command.")
        return False

    jarvis_speak("Starting transcript extraction and cleaning. This may take up to 30 seconds.")
    
    transcript_text = yt_summarize(full_url, lang=lang)
    
    if not transcript_text:
        jarvis_speak("Transcript extraction failed, or no English subtitles were found for that video.")
        return False
        
    # Example response (In a real LLM integration, the text would be sent for analysis)
    jarvis_speak(f"I successfully extracted a transcript of {len(transcript_text)} characters. The content is ready for analysis, and begins: {transcript_text[:100]}...")
    
    print("\n--- EXTRACTED YOUTUBE TRANSCRIPT (CLEAN) ---")
    print(transcript_text[:1000] + ("..." if len(transcript_text) > 1000 else ""))
    print("-----------------------------------")
    print(f"Total length: {len(transcript_text)} characters.")
    
    return True


# -------------------------------------------------------------
## CENTRALIZED SKILL MAP (References defined functions)
# -------------------------------------------------------------

SKILL_MAP = {
    # Text-Based Parsing Commands (Fast)
    "read pdf": handle_pdf_parse,
    "read document": handle_pdf_parse,
    "analyze pdf": handle_pdf_parse,

    # OCR-Based Parsing Commands (Slower, for Scanned Files)
    "ocr pdf": handle_pdf_ocr,
    "scan document": handle_pdf_ocr,
    "ocr document": handle_pdf_ocr,

    # NEW YOUTUBE SKILLS
    "what is this video": handle_yt_inspect,
    "inspect video": handle_yt_inspect,
    "get transcript": handle_yt_summarize,
    "summarize video": handle_yt_summarize,
}


# -------------------------------------------------------------
## Intent Router (The Scalable Function)
# -------------------------------------------------------------

def parse_command_for_intent(command):
    """
    Dynamically routes the user command to the appropriate skill function
    based on the Centralized Skill Map.
    """
    if command is None:
        return False
    
    # Ignore the command if the user simply repeats the confirmation prompt.
    if "how may i help" in command or "at your service" in command:
        print(f"LOGIC: Ignoring self-referential command: '{command}'")
        return True

    # --- DYNAMIC SKILL INVOCATION ---
    for keyword, skill_function in SKILL_MAP.items():
        if keyword in command:
            print(f"LOGIC: Matched keyword '{keyword}'. Executing {skill_function.__name__}...")
            # Execute the handler, passing the full command text
            skill_function(command) 
            return True
            
    # Default Error
    jarvis_speak("I am sorry, I did not recognize that command.")
    return False


# -------------------------------------------------------------
## Main Execution
# -------------------------------------------------------------

def main():
    start_tts_worker()
    r = sr.Recognizer()

    while True:
        active_recorder = wake_word_loop()          
        if active_recorder is None:
            print("Fatal Error: Could not initialize wake word or audio recorder.")
            speech_queue.put(None)
            return
        
        jarvis_speak("At your service. How may I help?")
        
        print("\n--- Transitioning to Active Command Listener ---")               
        command_text = listen_for_command(active_recorder, r)        
        
        if command_text:
            print(f"FINAL COMMAND RECEIVED: {command_text}")
            parse_command_for_intent(command_text)
        else:
            print("Command processing failed or was empty.")                  
        
        try:
            active_recorder.delete()
        except Exception as e:
            print(f"Warning: Could not delete recorder object. {e}")


if __name__ == "__main__":
    main()