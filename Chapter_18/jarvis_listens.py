import time
import subprocess
import pyttsx3 
import speech_recognition as sr
import webbrowser

# --- TTS CORE SETUP (From 2.1: Voice Director) ---
# NOTE: Using placeholder functions for jarvis_speak and set_jarvis_voice

engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 0.9)

def jarvis_speak(text, voice=None):     
    print(f"Jarvis Output: {text} [Spoken]")
    safe_text = text.replace("'", "''")
    cmd = [
        "powershell", "-NoProfile", "-Command", 
        f"Add-Type -AssemblyName System.Speech;\
          $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        f"$speak.Speak('{safe_text}')"
    ]

    
    # In a real environment, uncomment the line below to execute speech
    subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, 
    stderr=subprocess.DEVNULL) 
    
    time.sleep(len(text) / 200)

def set_jarvis_voice(user_voice="Zira"):    
    return "Microsoft David Desktop - English (United States)"

# --- STT CORE SETUP (From 2.2: The Acoustic Bridge) ---

r = sr.Recognizer() 
r.energy_threshold = 400 

def jarvis_listen():
    """Captures audio from the system's microphone."""
    with sr.Microphone() as source:
        print("--- Jarvis is Listening ---")
        jarvis_speak("Awaiting command.", voice_name)
        r.adjust_for_ambient_noise(source, duration=1.0)
        audio = r.listen(source)
        return audio

def convert_to_text(audio_data, voice_name=None):   
    text = ""
    try:        
        text = r.recognize_google(audio_data)
        print(f"User Command (Online/High-Accuracy): {text}")
        return text    
    except sr.RequestError:
        print("Jarvis: Network recognition failed. Attempting local mode...")
        try:            
            text = r.recognize_sphinx(audio_data)
            print(f"User Command (Offline/Local): {text}")
            return text
        except sr.UnknownValueError:
            jarvis_speak("Offline mode failed. Please speak clearly.", voice_name)
            return ""    
    except sr.UnknownValueError:
        jarvis_speak("Online recognition failed. " \
                     "I couldn't understand the audio.", voice_name)
        return ""
    
    

def execute_web_search(text, voice_name):    
    if text:
        search_url = f"https://www.google.com/search?q={text}"
        print(f"Jarvis: Executing search for '{text}'...")
        webbrowser.open(search_url)
        jarvis_speak(f"Search complete for {text}.", voice_name)

# --- MAIN EXECUTION FLOW (Demonstration) ---

voice_name = set_jarvis_voice("David") 

def main():    
    jarvis_speak("System check complete. Jarvis is now ready.", voice_name)    
    while True:
        try:            
            audio = jarvis_listen()
            command = convert_to_text(audio, voice_name)
        except sr.WaitTimeoutError:          
            command = ""        
        if command and "exit" in command.lower():
            break        
        if command:
            execute_web_search(command, voice_name)            
    
    jarvis_speak("System shutting down. Goodbye.", voice_name)

if __name__ == "__main__":   
    main()