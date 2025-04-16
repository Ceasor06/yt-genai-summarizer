import yt_dlp
import os
import uuid
import glob
import whisper
import re

model = whisper.load_model("base")  # You can change this to "small" or "medium"

# ---------- VIDEO ID EXTRACTOR ----------
def extract_video_id(youtube_url: str) -> str:
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, youtube_url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid YouTube URL: Could not extract video ID.")

# ---------- AUDIO DOWNLOADER ----------
def download_audio(youtube_url: str, output_dir: str = "temp_audio") -> tuple:
    os.makedirs(output_dir, exist_ok=True)
    filename = str(uuid.uuid4())
    output_path = os.path.join(output_dir, filename + ".%(ext)s")

    metadata_dict = {}

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'quiet': True,
        'sponsorblock-remove': ['sponsor', 'intro', 'outro', 'selfpromo'],
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'forcejson': True,
        'simulate': True,  # Only fetch metadata without downloading
    }

    # Extract metadata
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(youtube_url, download=False)
        metadata_dict = {
            "title": info_dict.get("title"),
            "uploader": info_dict.get("uploader"),
            "upload_date": info_dict.get("upload_date"),
            "duration": info_dict.get("duration"),
            "view_count": info_dict.get("view_count"),
            "like_count": info_dict.get("like_count"),
            "video_url": info_dict.get("webpage_url"),
            "thumbnail_url": info_dict.get("thumbnail")
        }

    # Actual download
    ydl_opts['simulate'] = False  # Enable downloading now
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

    matches = glob.glob(os.path.join(output_dir, f"{filename}*.mp3"))
    if not matches:
        raise FileNotFoundError("Audio file not found after download.")

    print("Download complete:", matches[0])
    return matches[0], metadata_dict


# ---------- TRANSCRIBE WITH CACHING ----------
def transcribe_audio_with_cache(youtube_url: str, audio_path: str, language: str, duration: int, cache_dir="transcripts") -> str:
    os.makedirs(cache_dir, exist_ok=True)
    video_id = extract_video_id(youtube_url)
    transcript_path = os.path.join(cache_dir, f"{video_id}_{language}.txt")

    if os.path.exists(transcript_path):
        print("Transcript loaded from cache.")
        with open(transcript_path, "r") as f:
            return f.read()

    model_name = select_whisper_model(language, duration)
    print(f"Selected Whisper model: {model_name}")
    model = whisper.load_model(model_name)

    result = model.transcribe(audio_path)
    transcript = result["text"]

    with open(transcript_path, "w") as f:
        f.write(transcript)

    # ✅ Auto-delete audio file after use
    try:
        os.remove(audio_path)
        print(f"Deleted audio file: {audio_path}")
    except Exception as e:
        print(f"Warning: Could not delete audio file {audio_path} — {e}")

    return transcript



def select_whisper_model(language: str, duration: int) -> str:
    if duration > 900:  # 900 seconds = 15 minutes
        return "base"  # Use fast model for long videos
    elif language != "en":
        return "large"  # Multilingual or complex, use high-accuracy
    else:
        return "small"

