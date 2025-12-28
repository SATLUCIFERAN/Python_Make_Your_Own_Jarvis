import subprocess
import os
import sys
from pathlib import Path
from typing import Optional

# Automatically finds the data folder relative to this script
ARCHIVE_DIR = Path(__file__).parent.parent / "data" / "archive_media"
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

if sys.platform.startswith('win'):
    _SUBPROCESS_FLAGS = subprocess.CREATE_NO_WINDOW
else:
    _SUBPROCESS_FLAGS = 0

# Try to find ffmpeg from imageio
def _get_ffmpeg_path():
    try:
        from imageio_ffmpeg import get_ffmpeg_exe
        return get_ffmpeg_exe()
    except ImportError:
        return "ffmpeg"

def _download_media_file(url: str, format_spec: str, ext: str, is_audio_only: bool) -> Optional[Path]:
    """
    Executes the yt-dlp download operation.
    """
    print(f"[{url}] -> Downloading to {ARCHIVE_DIR}...")
    
    output_template = str(ARCHIVE_DIR / "%(title)s.%(id)s.%(ext)s")
    ffmpeg_location = _get_ffmpeg_path()
    
    command = [
        "yt-dlp", 
        url, 
        "-f", format_spec,
        "--extractor-args", "youtube:player_client=android",
        "--ffmpeg-location", ffmpeg_location,
    ]
    
    if is_audio_only:
        command.extend([
            "-x",
            "--audio-format", ext
        ])
    else:
        command.extend([
            "--merge-output-format", ext
        ])

    command.extend([
        "--output", output_template,
    ])
    
    try:
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            encoding="utf-8", 
            errors="ignore",
            check=True, 
            timeout=300,
            creationflags=_SUBPROCESS_FLAGS
        )
        
        # Find the downloaded file by searching the archive directory
        matching_files = list(ARCHIVE_DIR.glob(f"*.{ext}"))
        
        if matching_files:
            # Get the most recently modified file
            saved_file_path = max(matching_files, key=lambda p: p.stat().st_mtime)
            print(f"SUCCESS: File saved to {saved_file_path.name}")
            return saved_file_path
        
        print("ERROR: Download finished but file not found.")
        return None
        
    except subprocess.TimeoutExpired:
        print("ERROR: Download timed out after 5 minutes.")
        return None
    except subprocess.CalledProcessError as e:
        print(f"ERROR: yt-dlp failed (Code {e.returncode}).")
        if e.stderr:
            print(f"Details: {e.stderr.strip()}")
        return None
    except FileNotFoundError:
        print("FATAL ERROR: 'yt-dlp' not found. Please install it.")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def yt_saveaudio(url: str) -> Optional[Path]:
    """
    Saves the video's audio track as an MP3 file.
    """
    print(f"[{url}] -> Initiating yt.saveaudio...")
    
    return _download_media_file(
        url=url, 
        format_spec="bestaudio/best", 
        ext="mp3",
        is_audio_only=True 
    )

def yt_savevideo(url: str) -> Optional[Path]:
    """
    Saves the full video (audio and video) as an MP4 file.
    """
    print(f"[{url}] -> Initiating yt.savevideo...")

    return _download_media_file(
        url=url, 
        format_spec="best[ext=mp4]/best", 
        ext="mp4",
        is_audio_only=False 
    )

if __name__ == "__main__":
    
    TEST_VIDEO_URL = "https://www.youtube.com/watch?v=GbUV3TXUzeQ" 
    
    print("\n" + "="*50)
    print("TESTING yt_saveaudio")
    print("="*50)
    
    audio_path = yt_saveaudio(TEST_VIDEO_URL) 
    
    if audio_path:
        print(f"Archived MP3: {audio_path}")
    else:
        print("Audio archiving failed.")

    print("\n" + "="*50)
    print("TESTING yt_savevideo")
    print("="*50)
    
    video_path = yt_savevideo(TEST_VIDEO_URL)
    
    if video_path:
        print(f"Archived MP4: {video_path}")
    else:
        print("Video archiving failed.")