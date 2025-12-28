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
    print("Warning: pyperclip not installed.")
    pyperclip = None

# --- CALENDAR SKILL IMPORT ---
from skills.calendar_tool import JarvisScheduler, ScheduleGUI, ListViewerGUI, ScheduleMonitor

# --- GLOBAL HARDWARE OBJECTS ---
global_recorder = None
global_recognizer = None
schedule_monitor = None  # Global monitor instance

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
    speech_queue = Queue()
else:
    import pyttsx3
    print(f"TTS Backend: pyttsx3 ({SYSTEM_OS})")
    tts_engine = None
    speech_queue = Queue()

# --- TTS INITIALIZATION ---

def initialize_tts_global():
    global tts_engine, tts_engine_win
    if SYSTEM_OS == "Windows":
        try:
            tts_engine_win = win32com.client.Dispatch("SAPI.SpVoice")
            tts_engine_win.Rate = 0 
            print("Windows TTS Client initialized.")
        except Exception as e:
            print(f"CRITICAL TTS FAILURE: {e}")
            tts_engine_win = None
    else:
        try:
            driver = 'nsss' if SYSTEM_OS == "Darwin" else 'espeak'
            tts_engine = pyttsx3.init(driver)
            rate = tts_engine.getProperty('rate')
            tts_engine.setProperty('rate', rate)
            print("pyttsx3 engine initialized.")
        except Exception as e:
            print(f"TTS Error: {e}") 
            tts_engine = None

initialize_tts_global()

# --- TTS WORKER THREAD ---

def _speak_pyttsx3(text):
    temp_engine = None
    try:
        driver = 'nsss' if SYSTEM_OS == "Darwin" else 'espeak'
        temp_engine = pyttsx3.init(driver)
        temp_engine.setProperty('rate', tts_engine.getProperty('rate'))
        temp_engine.say(text)
        temp_engine.startLoop(False) 
        time.sleep(0.5) 
    except Exception as e:
        print(f"[TTS Error - pyttsx3]: {e}")
    finally:
        if temp_engine:
            try:
                temp_engine.stop() 
                del temp_engine
            except:
                pass

def _speak_win32com(text):
    if tts_engine_win:
        try:
            tts_engine_win.Speak(text, 1)
            time.sleep(2)
        except Exception as e:
            print(f"[TTS Error - win32com]: {e}")

def tts_worker():
    print("[TTS Worker] Started")
    while True:
        text = speech_queue.get()
        if text is None: 
            break
        
        if SYSTEM_OS == "Windows":
            _speak_win32com(text)
        else:
            _speak_pyttsx3(text)
        
        speech_queue.task_done()

def start_tts_worker():
    is_ready = (SYSTEM_OS == "Windows" and tts_engine_win) or (SYSTEM_OS != "Windows" and tts_engine)
    if is_ready:
        worker = threading.Thread(target=tts_worker, daemon=True)
        worker.start()
        time.sleep(0.2)
        print("TTS Worker Thread Started")

def jarvis_speak(text): 
    """Queue text for speech output."""
    print(f"\n[JARVIS]: {text}\n")
    is_ready = (SYSTEM_OS == "Windows" and tts_engine_win) or (SYSTEM_OS != "Windows" and tts_engine)
    if is_ready:
        speech_queue.put(text)
    else: 
        print(f"[JARVIS SPEAKS (Fallback)]: {text}")

# --- CALENDAR SKILL SETUP ---
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
scheduler_engine = JarvisScheduler(DATA_DIR)

# --- NOTIFICATION CALLBACK ---
def on_schedule_notification(event):
    """Called by ScheduleMonitor when an event is approaching."""
    minutes = event['minutes_until']
    task = event['task']
    start_time = event['start_time']
    
    if minutes <= 0:
        message = f"Attention! Your appointment for {task} is starting now at {start_time}."
    elif minutes == 1:
        message = f"Reminder: Your appointment for {task} starts in 1 minute at {start_time}."
    else:
        message = f"Reminder: Your appointment for {task} starts in {minutes} minutes at {start_time}."
    
    jarvis_speak(message)
    print(f"[ALARM] {message}")

# --- START SCHEDULE MONITOR ---
def start_schedule_monitor():
    """Initialize and start the schedule monitoring system."""
    global schedule_monitor
    
    if schedule_monitor is None:
        schedule_monitor = ScheduleMonitor(scheduler_engine, on_schedule_notification)
        schedule_monitor.start()
        print("[System] Schedule Monitor activated")

# --- CALENDAR HANDLERS ---

def handle_calendar_open(command):
    jarvis_speak("Opening your visual scheduler now.")
    try:
        app = ScheduleGUI(scheduler_engine)
        saved_data = app.run() 
        if saved_data:
            response = (f"Confirming: I have scheduled your {saved_data['task']} "
                        f"for {saved_data['date']} at {saved_data['start']}. "
                        f"I will remind you {saved_data['reminder']} minutes before.")
            jarvis_speak(response)
        else:
            jarvis_speak("The scheduling session was cancelled.")
    except Exception as e:
        jarvis_speak("I encountered an error opening the calendar.")
        print(f"Calendar Error: {e}")
    return True

def handle_view_schedule(command):
    events = scheduler_engine.get_all_events()
    if not events:
        jarvis_speak("Your schedule is currently empty.")
        return True

    jarvis_speak(f"I found {len(events)} items. Opening the visual log now.")
    
    def launch_gui():
        viewer = ListViewerGUI(scheduler_engine)
        viewer.run()

    gui_thread = threading.Thread(target=launch_gui, daemon=True)
    gui_thread.start()
    
    return True

def handle_calendar_delete(command):
    global global_recorder, global_recognizer
    
    target = command.replace("cancel", "").replace("delete", "").replace("remove", "").strip()
    
    if not target:
        jarvis_speak("Which appointment should I cancel?")
        target = listen_for_command(global_recorder, global_recognizer) 
        
        if not target or target == "none":
            jarvis_speak("I didn't catch that. Cancellation aborted.")
            return True

    if scheduler_engine.delete_event_by_name(target):
        jarvis_speak(f"I have successfully removed {target} from your schedule.")
    else:
        jarvis_speak(f"I could not find any appointments matching {target}.")
    return True

def handle_upcoming_events(command):
    """Tell user about upcoming events."""
    upcoming = scheduler_engine.get_upcoming_events(minutes_ahead=120)
    
    if not upcoming:
        jarvis_speak("You have no upcoming appointments in the next 2 hours.")
        return True
    
    if len(upcoming) == 1:
        event = upcoming[0]
        minutes = event['minutes_until']
        task = event['task']
        
        if minutes <= 0:
            jarvis_speak(f"Your appointment for {task} is starting now.")
        elif minutes <= 15:
            jarvis_speak(f"You have {task} starting in {minutes} minutes.")
        else:
            jarvis_speak(f"Your next appointment is {task} in {minutes} minutes.")
    else:
        jarvis_speak(f"You have {len(upcoming)} upcoming appointments.")
        for i, event in enumerate(upcoming[:3], 1):  # Show first 3
            minutes = event['minutes_until']
            task = event['task']
            jarvis_speak(f"Number {i}: {task} in {minutes} minutes.")
    
    return True

def handle_silence_alarms(command):
    """Temporarily silence alarms."""
    jarvis_speak("I will silence schedule reminders for the next 30 minutes.")
    # TODO: Implement temporary silence
    return True

def handle_reset_notifications(command):
    """Reset all notification flags (for testing)."""
    if scheduler_engine.reset_all_notifications():
        jarvis_speak("All notification flags have been reset.")
    else:
        jarvis_speak("Failed to reset notifications.")
    return True

# --- WAKE WORD ENGINE ---
ACCESS_KEY = os.environ.get("PICOVOICE_ACCESS_KEY")
WAKE_WORD = "jarvis" 

def wake_word_loop():
    if not ACCESS_KEY:
        print("ERROR: PICOVOICE_ACCESS_KEY not set.")
        return None
    try:
        porcupine = pvporcupine.create(access_key=ACCESS_KEY, keywords=[WAKE_WORD])
    except Exception as e:
        print(f"Porcupine Error: {e}")
        return None

    recorder = PvRecorder(frame_length=porcupine.frame_length, device_index=-1)
    recorder.start()
    print(f"Listening passively for '{WAKE_WORD}'...")

    try:
        while True: 
            pcm = recorder.read() 
            if porcupine.process(pcm) >= 0:
                print(f"Wake Word Detected: {WAKE_WORD.upper()}!")
                break 
    finally:   
        porcupine.delete()  
    return recorder 

# --- STT COMMAND LISTENER ---
def listen_for_command(recorder, recognizer):
    if not recorder: 
        return None 
    
    recorder.stop()
    speech_queue.join() 
    time.sleep(0.3)

    with sr.Microphone() as source:
        print("--- JARVIS: Active Listening State. Speak Now... ---")
        recognizer.adjust_for_ambient_noise(source, duration=1.0) 
        try:   
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=8)   
            command = recognizer.recognize_google(audio)
            return command.lower()
        except sr.WaitTimeoutError:
            print("--- Timeout ---")
            return None
        except sr.UnknownValueError:
            print("--- Unknown Value ---")
            return None
        except sr.RequestError as e:
            print(f"--- STT Error: {e} ---")
            return None

# --- INTENT ROUTING ---
SKILL_MAP = {
    "view meeting": handle_view_schedule,
    "show my schedule": handle_view_schedule,
    "list my tasks": handle_view_schedule,
    "view schedule": handle_view_schedule,
    "show schedule": handle_view_schedule,
    
    "schedule": handle_calendar_open,
    "calendar": handle_calendar_open,
    "appointment": handle_calendar_open,
    "add task": handle_calendar_open,
    
    "delete": handle_calendar_delete,
    "remove": handle_calendar_delete,
    "cancel": handle_calendar_delete,
    
    "what's next": handle_upcoming_events,
    "what's coming up": handle_upcoming_events,
    "upcoming": handle_upcoming_events,
    "next appointment": handle_upcoming_events,
    
    "silence alarms": handle_silence_alarms,
    "stop reminders": handle_silence_alarms,
    
    "reset notifications": handle_reset_notifications,
}

def parse_command_for_intent(command):
    if command is None: 
        return False
    
    if "how may i help" in command or "at your service" in command: 
        return True

    for keyword, skill_function in SKILL_MAP.items():
        if keyword in command:
            print(f"[LOGIC] Matched: '{keyword}'")
            skill_function(command)
            return True
            
    jarvis_speak("I am sorry, I did not recognize that command.")
    return False

# --- MAIN LOOP ---
def main():
    global global_recorder, global_recognizer
    
    start_tts_worker()
    start_schedule_monitor()  # Start monitoring schedules
    
    r = sr.Recognizer()
    global_recognizer = r

    print("\n" + "="*60)
    print("  JARVIS INTELLIGENT ASSISTANT")
    print("  - Voice Commands Active")
    print("  - Schedule Monitoring Active")
    print("  - Say 'Jarvis' to activate")
    print("="*60 + "\n")

    while True:
        active_recorder = wake_word_loop() 
        if active_recorder is None:
            speech_queue.put(None)
            return
        
        global_recorder = active_recorder
        
        jarvis_speak("At your service. How may I help?")
        command_text = listen_for_command(active_recorder, r) 
        
        if command_text:
            print(f"[COMMAND]: {command_text}")
            parse_command_for_intent(command_text)
        
        try:
            active_recorder.delete()
        except:
            pass

if __name__ == "__main__":
    main()