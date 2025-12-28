import os
import pvporcupine
from pvrecorder import PvRecorder
import pyttsx3
import threading 
import speech_recognition as sr 

# --- 1. PYTTSX3 INITIALIZATION (Global Scope) ---

try: 
    tts_engine = pyttsx3.init() 
    rate = tts_engine.getProperty('rate')
    tts_engine.setProperty('rate', rate - 30) 
except Exception as e:
    print(f"Jarvis TTS Error: Failed to initialize pyttsx3 engine. Error: {e}") 
    tts_engine = None


def jarvis_speak(text): 
    # This function is BLOCKING (it waits for audio to finish), 
    # but that's okay because it runs in its own non-blocking thread.
    if tts_engine:  
        tts_engine.say(text)  
        tts_engine.runAndWait()
    else:  
        print(f"\n[JARVIS SPEAKS (Fallback)]: {text}\n")


# -------------------------------------------------------------
##  Wake Word Engine Functions 
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

    # Initialize the audio recorder
    recorder = PvRecorder(
        frame_length=porcupine.frame_length,
        device_index=-1 
    )
    recorder.start()
    print(f"🔊 Listening passively for '{WAKE_WORD}'...")
    
    try:
        while True:  
            pcm = recorder.read()  
            keyword_index = porcupine.process(pcm)              
            if keyword_index >= 0:
                print(f"Wake Word Detected: {WAKE_WORD.upper()}!")                  
                tts_thread = threading.Thread(
                    target=jarvis_speak, 
                    args=("At your service. How may I help?",)
                )
                tts_thread.start()
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
    
    with sr.Microphone() as source:
        print("--- JARVIS: Active Listening State. Speak Now... ---")
        recognizer.adjust_for_ambient_noise(source) 
        
        try:            
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)            
            command = recognizer.recognize_google(audio)
            print("---  JARVIS: Processing audio... ---")
            return command.lower()
            
        except sr.WaitTimeoutError:
            print("---  Timeout: No command heard. ---")
            return None
        except sr.UnknownValueError:
            print("---  Unknown Value: Could not understand audio. ---")
            return None
        except sr.RequestError as e:
            print(f"---  STT Error: Could not request results from Google; {e} ---")
            return None

# The convert_to_text and old jarvis_listen placeholders are now obsolete.

def main():  
    
    r = sr.Recognizer()   
    active_recorder = wake_word_loop()     
    if active_recorder is None:
        print(" Fatal Error: " \
              "Could not initialize wake word or audio recorder. Exiting.")
        return
    
    
    print("\n--- Transitioning to Active Command Listener ---")    
    command_text = listen_for_command(active_recorder, r)    
    if command_text:
        print(f" FINAL COMMAND RECEIVED: {command_text}")
    else:
        print(" Command processing failed or was empty.")        
    
    try:
        active_recorder.delete()
    except Exception as e:
        print(f"Warning: Could not delete recorder object. {e}")
        
    print("--- Test Scenario Complete ---")


if __name__ == "__main__":
    main()