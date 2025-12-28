from datetime import datetime
import time
import subprocess
import pyttsx3 

# --- CORE FUNCTIONS ---

# Initialize pyttsx3 for reference (rate/volume/voice)

engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 0.9)

def set_jarvis_voice(user_voice="Zira"): 
    voices = engine.getProperty('voices')
    if not voices:
        print("\nFATAL ERROR: No speech voices found on this system.")
        return "Microsoft David Desktop - English (United States)" 

    selected_id = None
    print("\n--- Available Voices (reference only) ---")
    for i, voice in enumerate(voices):
        print(f"Voice {i}: Name='{voice.name}', ID='{voice.id}'")
        if user_voice.lower() in voice.name.lower():
            selected_id = voice.id
            break

    if selected_id:
        engine.setProperty('voice', selected_id)
        print(f"\nREFERENCE: pyttsx3 voice selection set to: {user_voice} "
              f"(may not match actual spoken voice).")
        return user_voice
    else:
        engine.setProperty('voice', voices[0].id)
        print(f"\nREFERENCE: pyttsx3 custom voice not found.\
              Using primary system default: {voices[0].name}")
        return voices[0].name 
    
def jarvis_speak(text, voice=None): 
    if voice is None:
        voice = "Microsoft David Desktop - English (United States)" 
    print(f"Jarvis Output: {text}")
    safe_text = text.replace("'", "''")   
    fallback_index = 1 
    if "david" in voice.lower():
        fallback_index = 0 
    cmd = [
        "powershell",
        "-NoProfile",
        "-Command",        
        f"Add-Type -AssemblyName System.Speech; "
        f"$speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        f"$available = $speak.GetInstalledVoices() | ForEach-Object {{$_.VoiceInfo.Name}}; "        
        f"if ($available -contains '{voice}') {{$speak.SelectVoice('{voice}')}}\
          else {{$speak.SelectVoice($available[{fallback_index}])}};"        
        f"$speak.Speak('{safe_text}')"
    ]
    subprocess.run(cmd, check=False)

def execute_time_report(voice=None): 
    now = datetime.now()
    date_string = now.strftime("%A, %B %d, %Y")
    time_string = now.strftime("%I:%M %p")
    message = (
        f"Verifying system status. Today is {date_string}, "
        f"and the current time is {time_string}."
    )
    jarvis_speak(message, voice)

# --- MAIN EXECUTION FLOW ---

def main(user_voice="Zira"): 
    # set_jarvis_voice returns the full, validated voice name (e.g., "Microsoft David...")
    voice_name = set_jarvis_voice(user_voice) 
    
    # voice_name is passed to jarvis_speak
    jarvis_speak("Hello, Sir. Jarvis is online and awaiting command.", voice_name)
    time.sleep(0.5) 
    execute_time_report(voice_name)

if __name__ == "__main__":
    # Test 1: Set to David (should force fallback to Index 0)
    main(user_voice="David") 
    
    # You can comment out the line above and uncomment the line below 
    # to test Zira again, which should force fallback to Index 1
    # main(user_voice="Zira")