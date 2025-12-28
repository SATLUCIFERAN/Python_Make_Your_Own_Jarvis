
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
    import pyperclip
except ImportError:
    print("Warning: pyperclip not installed. Install with 'pip install pyperclip' for clipboard integration.")
    pyperclip = None

# --- MODULAR SKILL IMPORTS ---
from skills.pdf_parser import pdf_parse
from skills.pdf_ocr import image_ocr
from skills.yt_tools import yt_inspect, yt_summarize
from skills.yt_tools_archival import yt_saveaudio, yt_savevideo
from skills.web_tools import scrape_url_for_selector
# NEW: Import the Dynamic Archivist Tool
from skills.dynamic_tools import scrape_dynamic_site 

# --- CONDITIONAL IMPORTS ---
SYSTEM_OS = platform.system()
if SYSTEM_OS == "Windows":
    try:
        import win32com.client
        print("TTS Backend: win32com (Windows)")
    except ImportError:
        print("FATAL ERROR: win32com.client not found. Install with 'pip install pywin32'")
        exit()
    tts_engine_win = None
    engine_driver_name = 'sapi5'
    speech_queue = Queue()
else:
    import pyttsx3
    print(f"TTS Backend: pyttsx3 ({SYSTEM_OS})")
    tts_engine = None
    speech_queue = Queue()
    if SYSTEM_OS == "Darwin":
        engine_driver_name = 'nsss'
    else:
        engine_driver_name = 'espeak'

# --- 1. TTS INITIALIZATION (OS Specific) ---

def initialize_tts_global():
    global tts_engine, tts_engine_win

    if SYSTEM_OS == "Windows":
        try:
            tts_engine_win = win32com.client.Dispatch("SAPI.SpVoice")
            tts_engine_win.Rate = 0 
            print("Windows TTS Client initialized. Rate set to 0 (Default).")
        except Exception as e:
            print(f"CRITICAL TTS FAILURE (win32com): {e}")
            tts_engine_win = None
    else:
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
            tts_engine_win.Speak(text, 1)
            time.sleep(2)
            
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
        speech_queue.task_done()


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
    time.sleep(0.3)

    with sr.Microphone() as source:
        print("--- JARVIS: Active Listening State. Speak Now... ---")
        recognizer.adjust_for_ambient_noise(source) 
        
        try:   
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)   
            command = recognizer.recognize_google(audio)
            print("--- JARVIS: Processing audio... ---")
            return command.lower()
            
        except sr.WaitTimeoutError:
            print("--- Timeout: No command heard. ---")
            return None
        except sr.UnknownValueError:
            print("--- Unknown Value: Could not understand audio. ---")
            return None
        except sr.RequestError as e:
            print(f"--- STT Error: Could not request results from Google; {e} ---")
            return None


# -------------------------------------------------------------
## WEB SCRAPING SKILLS (STATIC AND DYNAMIC)
# -------------------------------------------------------------
WEB_URL_REGEX = r'https?://[^\s"\']+'
WEB_SELECTOR_REGEX = r'["\']([^"\']+)["\']' 

def handle_web_scrape(command):
    """
    Uses regex to extract the URL and an OPTIONAL CSS selector from the command.
    Uses a sensible default selector if none is provided.
    """
    url_match = re.search(WEB_URL_REGEX, command)
    full_url = url_match.group(0) if url_match else None
    
    if not full_url and pyperclip:
        try:
            clipboard_content = pyperclip.paste()
            clipboard_match = re.search(WEB_URL_REGEX, clipboard_content)
            if clipboard_match:
                full_url = clipboard_match.group(0)
                jarvis_speak("Found a URL on the clipboard.")
        except:
            pass
            
    selector_match = re.search(WEB_SELECTOR_REGEX, command)
    selector = selector_match.group(1) if selector_match else None
    
    if not full_url:
        jarvis_speak("I could not find a URL in your command or on the clipboard.")
        return False
        
    if not selector:
        selector = 'p, h1, h2, h3, li' 
        jarvis_speak("No specific selector was provided. I will attempt to extract main headings, paragraphs, and list items.")
        
    jarvis_speak(f"Starting ethical web scrape on the provided URL, looking for the element: {selector}.")
    
    elements = scrape_url_for_selector(full_url, selector)
    
    if elements is None:
        jarvis_speak("The website's robots policy denied access, or a network error occurred. Scraping aborted ethically.")
    elif not elements:
        jarvis_speak(f"I fetched the page, but I couldn't find any elements matching '{selector}'. Check your selector syntax.")
    else:
        first_texts = []
        for text in elements: # Loop through ALL elements
            if text and text.strip(): # Check if text is present and non-whitespace
                first_texts.append(text.strip())
                if len(first_texts) >= 5: # Stop only when 5 *meaningful* pieces are found
                    break
        
        if first_texts:
            extracted_text = " | ".join(first_texts)
        else:
            extracted_text = "The first elements were found but contained no readable text."
            
        response = (
            f"Successfully extracted {len(elements)} elements. The first results are: {extracted_text[:200]}. "
            "The full data is printed to the console."
        )
        jarvis_speak(response)
        
        print(f"\n--- EXTRACTED WEB CONTENT ({len(elements)} items) ---")
        for i, text in enumerate(elements, 1):
            if text:
                print(f"{i}. {text[:100]}...")
        print("-----------------------------------")
    
    return True

# --- NEW SKILL INTEGRATION: DYNAMIC SCRAPING HANDLER ---
def handle_dynamic_scrape(command):
    """
    Handles JavaScript-heavy sites by launching a headless browser.
    Extracts text, links, and automatically archives media.
    """
    url_match = re.search(WEB_URL_REGEX, command)
    full_url = url_match.group(0) if url_match else None
    
    # Clipboard Fallback
    if not full_url and pyperclip:
        try:
            clipboard_content = pyperclip.paste()
            clipboard_match = re.search(WEB_URL_REGEX, clipboard_content)
            if clipboard_match:
                full_url = clipboard_match.group(0)
                jarvis_speak("Found a URL on the clipboard for deep search.")
        except:
            pass
            
    selector_match = re.search(WEB_SELECTOR_REGEX, command)
    selector = selector_match.group(1) if selector_match else None
    
    if not full_url:
        jarvis_speak("Please provide a URL or copy one to your clipboard for a deep search.")
        return False
        
    if not selector:
        # selector = "p, h1, h2, h3, li" # sensible default for testing
        selector = "a.ExploreCard__Link" 
        jarvis_speak("Using default header selector for the deep search.")
        
    jarvis_speak("Initializing headless browser for deep search and image archival. This will take a moment.")
    
    results = scrape_dynamic_site(full_url, selector)
    
    if results:
        count = len(results)
        # Extract the first 5 titles for spoken feedback
        top_titles = [item['text'] for item in results[:5]]
        extracted_text = " | ".join(top_titles)
        
        response = (
            f"Deep search complete. I found {count} items and archived relevant media to your data folder. "
            f"The primary results are: {extracted_text}"
        )
        jarvis_speak(response)
        
        print(f"\n--- DYNAMIC DATA ARCHIVED ({count} items) ---")
        for i, item in enumerate(results[:10], 1):
            print(f"{i}. {item['text']}")
            print(f"   Image Path: {item['local_path']}")
        print("-----------------------------------")
    else:
        jarvis_speak("The deep search timed out or found no data. Please check the debug view screenshot.")
    
    return True

# -------------------------------------------------------------
## PDF PARSING SKILLS
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

def handle_pdf_ocr(command, file_name="data/scanned_sample.png"):
    """Reads PDF using the slow, image-based OCR method (image_ocr)."""
    file_path = Path(__file__).parent / file_name

    if not file_path.exists():
        jarvis_speak(f"Error: The scanned document {file_path.name} was not found.")
        return False
    
    jarvis_speak(f"Starting OCR process on {file_path.name}. This may take a moment.")

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
## YOUTUBE SKILLS
# -------------------------------------------------------------

def handle_yt_inspect(command):
    """
    Extracts metadata from a YouTube URL found in the command text, 
    falling back to checking the system clipboard.
    """
    url_match = re.search(r'https?://(?:www\.)?(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|v/))([\w-]{11})', command)
    full_url = None
    
    if url_match:
        full_url = url_match.group(0)
    elif pyperclip:
        try:
            clipboard_content = pyperclip.paste()
            clipboard_match = re.search(r'https?://(?:www\.)?(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|v/))([\w-]{11})', clipboard_content)
            if clipboard_match:
                full_url = clipboard_match.group(0)
                jarvis_speak("Found a YouTube link on your clipboard. Proceeding with inspection.")
            else:
                print("LOGIC: Clipboard content was not a YouTube URL.")
        except Exception as e:
            print(f"Warning: Could not read clipboard. Error: {e}")

    if not full_url:
        jarvis_speak("Please copy a valid YouTube link to your clipboard and try again, or include the link in your command.")
        return False
        
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

def handle_yt_summarize(command, lang="en"):
    """
    Extracts the full transcript from a YouTube URL found in the command text,
    with clipboard fallback.
    """
    url_match = re.search(r'https?://(?:www\.)?(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|v/))([\w-]{11})', command)
    full_url = None
    
    if url_match:
        full_url = url_match.group(0)
    elif pyperclip:
        try:
            clipboard_content = pyperclip.paste()
            clipboard_match = re.search(r'https?://(?:www\.)?(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|v/))([\w-]{11})', clipboard_content)
            if clipboard_match:
                full_url = clipboard_match.group(0)
                jarvis_speak("Found a YouTube link on your clipboard.")
        except:
            pass

    if not full_url:
        jarvis_speak("Please copy a valid YouTube link to your clipboard and try again, or include the link in your command.")
        return False

    jarvis_speak("Starting transcript extraction and cleaning. This may take up to 30 seconds.")
    
    transcript_text = yt_summarize(full_url, lang=lang)
    
    if not transcript_text:
        jarvis_speak("Transcript extraction failed, or no English subtitles were found for that video.")
        return False
        
    jarvis_speak(f"I successfully extracted a transcript of {len(transcript_text)} characters. The content is ready for analysis, and begins: {transcript_text[:100]}...")
    
    print("\n--- EXTRACTED YOUTUBE TRANSCRIPT (CLEAN) ---")
    print(transcript_text[:1000] + ("..." if len(transcript_text) > 1000 else ""))
    print("-----------------------------------")
    print(f"Total length: {len(transcript_text)} characters.")
    
    return True

def handle_yt_saveaudio(command):
    """
    Downloads the audio of a YouTube video using the URL found in the 
    command text or clipboard, and archives it as an MP3.
    """
    url_match = re.search(r'https?://(?:www\.)?(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|v/))([\w-]{11})', command)
    full_url = None
    
    if url_match:
        full_url = url_match.group(0)
    elif pyperclip:
        try:
            clipboard_content = pyperclip.paste()
            clipboard_match = re.search(r'https?://(?:www\.)?(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|v/))([\w-]{11})', clipboard_content)
            if clipboard_match:
                full_url = clipboard_match.group(0)
                jarvis_speak("Found a YouTube link on your clipboard. Starting audio download.")
        except Exception as e:
            print(f"Warning: Could not read clipboard. Error: {e}")

    if not full_url:
        jarvis_speak("Please copy a valid YouTube link to your clipboard and try again, or include the link in your command.")
        return False
        
    jarvis_speak(f"Starting heavy audio download and conversion for archival. This will take a moment.")
    
    saved_path = yt_saveaudio(full_url)
    
    if saved_path:
        jarvis_speak(f"Audio file successfully archived as MP3. The file is saved locally.")
        print(f"Archived file location: {saved_path.resolve()}")
    else:
        jarvis_speak("Audio download failed. Check yt-dlp and ffmpeg configuration.")
        
    return True

def handle_yt_savevideo(command):
    """
    Downloads the video of a YouTube video using the URL found in the 
    command text or clipboard, and archives it as an MP4.
    """
    url_match = re.search(r'https?://(?:www\.)?(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|v/))([\w-]{11})', command)
    full_url = None
    
    if url_match:
        full_url = url_match.group(0)
    elif pyperclip:
        try:
            clipboard_content = pyperclip.paste()
            clipboard_match = re.search(r'https?://(?:www\.)?(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|v/))([\w-]{11})', clipboard_content)
            if clipboard_match:
                full_url = clipboard_match.group(0)
                jarvis_speak("Found a YouTube link on your clipboard. Starting video download.")
        except Exception as e:
            print(f"Warning: Could not read clipboard. Error: {e}")

    if not full_url:
        jarvis_speak("Please copy a valid YouTube link to your clipboard and try again, or include the link in your command.")
        return False
        
    jarvis_speak(f"Starting heavy video download and merge for archival. This will take a moment.")
    
    saved_path = yt_savevideo(full_url)
    
    if saved_path:
        jarvis_speak(f"Video file successfully archived as MP4. The file is saved locally.")
        print(f"Archived file location: {saved_path.resolve()}")
    else:
        jarvis_speak("Video download failed. Check yt-dlp and ffmpeg configuration.")
        
    return True


# -------------------------------------------------------------
## CENTRALIZED SKILL MAP (References defined functions)
# -------------------------------------------------------------

SKILL_MAP = {
    "scrape web": handle_web_scrape,
    "get web data": handle_web_scrape,
    "extract data": handle_web_scrape,

    # NEW SKILL TRIGGERS: DYNAMIC SCRAPING
    "research": handle_dynamic_scrape,      
    "full scan": handle_dynamic_scrape,     
    "dig deeper": handle_dynamic_scrape,    
    "advanced search": handle_dynamic_scrape,
    
    "read pdf": handle_pdf_parse,
    "read document": handle_pdf_parse,
    "analyze pdf": handle_pdf_parse,

    "ocr pdf": handle_pdf_ocr,
    "scan document": handle_pdf_ocr,
    "ocr document": handle_pdf_ocr,

    "what is this video": handle_yt_inspect,
    "inspect video": handle_yt_inspect,
    "get transcript": handle_yt_summarize,
    "summarize video": handle_yt_summarize,

    "download audio": handle_yt_saveaudio,
    "archive audio": handle_yt_saveaudio,
    "download video": handle_yt_savevideo,
    "archive video": handle_yt_savevideo,
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
    
    if "how may i help" in command or "at your service" in command:
        print(f"LOGIC: Ignoring self-referential command: '{command}'")
        return True

    for keyword, skill_function in SKILL_MAP.items():
        if keyword in command:
            print(f"LOGIC: Matched keyword '{keyword}'. Executing {skill_function.__name__}...")
            skill_function(command) 
            return True
            
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