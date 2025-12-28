
import os
import pvporcupine
from pvrecorder import PvRecorder
import pyttsx3

# --- 1. PYTTSX3 INITIALIZATION (Global Scope) ---

try:    
    tts_engine = pyttsx3.init()    
    rate = tts_engine.getProperty('rate')
    tts_engine.setProperty('rate', rate - 30) 
except Exception as e:
    print(f"Jarvis TTS Error: Failed to initialize pyttsx3 engine. Error: {e}")    
    tts_engine = None


def jarvis_speak(text):    
    if tts_engine:        
        tts_engine.say(text)        
        tts_engine.runAndWait()
    else:        
        print(f"\n[JARVIS SPEAKS (Fallback)]: {text}\n")


# -------------------------------------------------------------
## 9. NEW: Wake Word Engine Functions (Section 3.1)
# -------------------------------------------------------------

ACCESS_KEY = os.environ.get("PICOVOICE_ACCESS_KEY")
WAKE_WORD = "jarvis" 

def wake_word_loop():
    
    if not ACCESS_KEY:
        print("Jarvis ERROR: PICOVOICE_ACCESS_KEY environment variable not set.")
        print("Please set the variable and restart the application.")
        return

    # Load the Porcupine engine for the specified keyword

    try:
        porcupine = pvporcupine.create(
            access_key=ACCESS_KEY,
            keywords=[WAKE_WORD]
        )
    except Exception as e:
        print(f"Jarvis ERROR: Failed to initialize Porcupine.\
              Check ACCESS_KEY validity. Error: {e}")
        return

    # Initialize the audio recorder using Porcupine's required frame length

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
                recorder.stop()               
                jarvis_speak("At your service. How may I help?")                
                break   
    finally:    
        porcupine.delete()

        # recorder.stop() is already handled inside the detection block.

# -------------------------------------------------------------
## 10. Main Execution for Wake Word Testing
# -------------------------------------------------------------

def main():    
    wake_word_loop() 

if __name__ == "__main__":
    main()