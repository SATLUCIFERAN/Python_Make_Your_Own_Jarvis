
import subprocess
import json
import os
import re
from pathlib import Path
import sys 

# --- Configuration ---
# IMPORTANT: This assumes 'yt-dlp' is installed and accessible in your system's PATH.
# Installation: pip install yt-dlp 

# --- ROBUSTNESS FIX FOR WINDOWS I/O DEADLOCKS ---
# CREATE_NO_WINDOW prevents console I/O deadlocks/hangs when capturing output on Windows.

if sys.platform.startswith('win'):
    _SUBPROCESS_FLAGS = subprocess.CREATE_NO_WINDOW
else:
    _SUBPROCESS_FLAGS = 0 


# ------------------------------------------------

def yt_inspect(url: str) -> dict | None:   
    print(f"[{url}] -> Inspecting metadata...")
    command = [
        "yt-dlp", 
        url, 
        "--dump-json",     
        "--skip-download"  
    ]

    try:        
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True,
            encoding="utf-8", 
            errors="ignore", 
            check=True,
            timeout=15, 
            creationflags=_SUBPROCESS_FLAGS
        )   

        metadata = json.loads(result.stdout)        
        return {
            "title": metadata.get("title", "N/A"),
            "duration": metadata.get("duration_string", "N/A"),
            "channel": metadata.get("channel", "N/A"),
            "thumbnail_url": metadata.get("thumbnail", "N/A") 
        }

    except subprocess.TimeoutExpired:
        print("ERROR: yt-dlp operation timed out after 15 seconds.")
        return None
    except subprocess.CalledProcessError as e:
        print(f"ERROR: yt-dlp failed (Code {e.returncode}). Is the URL valid?")
        print(f"yt-dlp STDERR: {e.stderr.strip()}")
        return None
    except FileNotFoundError:
        print("FATAL ERROR: 'yt-dlp' command not found. Install it or check PATH.")
        return None
    except json.JSONDecodeError:
        print("ERROR: Failed to decode JSON from yt-dlp output.")
        return None


def yt_summarize(url: str, lang: str = "en") -> str | None:    
    print(f"[{url}] -> Extracting '{lang}' transcript...")    
    temp_dir = Path("./temp_yt_subs")
    temp_dir.mkdir(exist_ok=True)    
    output_template = str(temp_dir / "%(title)s.%(id)s.%(autonumber)s.%(ext)s")
    
    command = [
        "yt-dlp", 
        url,
        "--skip-download",          
        "--write-auto-subs",        
        "--write-subs",             
        f"--sub-langs", lang,       
        "--convert-subs", "vtt",    
        "--output", output_template 
    ]

    try:        
        subprocess.run(
            command, 
            check=True, 
            capture_output=True, 
            text=True, 
            encoding="utf-8",
            errors="ignore", 
            timeout=30, 
            creationflags=_SUBPROCESS_FLAGS
        )
        
        # Step 2: Find the downloaded subtitle file (yt-dlp names it based on the template)

        subtitle_files = list(temp_dir.glob("*.vtt"))
        if not subtitle_files:
            print(f"WARNING: No '{lang}' subtitles found for this video.\
                  (Check language code or if subs exist)")
            return None            
        vtt_file_path = subtitle_files[0]
        
        # Step 3: Read and clean the VTT file

        with open(vtt_file_path, 'r', encoding='utf-8') as f:
            vtt_content = f.read()

        # START OF REFINED CLEANING AND DEDUPLICATION LOGIC

        # 1. Remove VTT header and timestamps

        clean_text = re.sub(r'WEBVTT.*?\n\n', '', vtt_content, flags=re.DOTALL)
        clean_text = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3}.*?\n', '', clean_text) 
        
        
        clean_text = re.sub(r'<[^>]*>', '', clean_text)
        clean_text = clean_text.replace('<', '').replace('>', '') 

        
        lines = [line.strip() for line in clean_text.split('\n') if line.strip()]
        unique_lines = []
        seen_content = set()

        for line in lines:            
            comparison_line = re.sub(r'[^\w\s]', '', line).lower()            
            if comparison_line and comparison_line not in seen_content:
                unique_lines.append(line)
                seen_content.add(comparison_line) 


        final_text = ' '.join(unique_lines)         
        return final_text
    
        # END OF REFINED CLEANING AND DEDUPLICATION LOGIC

    except subprocess.TimeoutExpired:
        print("ERROR: Subtitle download operation timed out after 30 seconds.")
        return None
    except subprocess.CalledProcessError as e:        
        print(f"ERROR: Subtitle download failed. STDERR:\n{e.stderr.strip()}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
    finally:        
        try:
            for f in temp_dir.glob("*"):
                os.remove(f)
            temp_dir.rmdir()
            print("Cleanup successful.")
        except Exception as e:            
            print(f"WARNING: Cleanup failed: {e}")

# --- Example Usage (Testing the Skills) ---

if __name__ == "__main__":    
    TEST_VIDEO_URL = "https://www.youtube.com/watch?v=px2hdZJLC3A" 

    print("\n" + "="*50)
    print("Testing : yt_inspect (Metadata)")
    print("="*50)
    
    metadata = yt_inspect(TEST_VIDEO_URL)    
    if metadata:
        print("\n--- Jarvis's Instant Video Intel ---")
        print(f"Title: {metadata['title']}")
        print(f"Duration: {metadata['duration']}")
        print(f"Channel: {metadata['channel']}")
        print("------------------------------------")
    
    print("\n" + "="*50)
    print("Testing New Skill : yt_summarize (Transcript)")
    print("="*50)    
    transcript = yt_summarize(TEST_VIDEO_URL, lang="en") 
    
    if transcript:
        print("\n--- Transcript Snippet (Ready for LLM) ---")        
        print(transcript[:500] + "\n...") 
        print(f"\nTotal characters: {len(transcript)}")
        print("------------------------------------------")
    else:
        print("Could not retrieve transcript.")