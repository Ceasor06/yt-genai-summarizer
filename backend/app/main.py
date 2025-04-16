from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from .logger import log_request
import os

from app.utils import (
    download_audio,
    transcribe_audio_with_cache,
    extract_video_id,
)
from app.summarize import (
    gpt_summary,
    load_summary_from_cache,
    save_summary_to_cache,
    translate_text,
    save_files,
)

from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

# Serve static files for downloads
app.mount("/files", StaticFiles(directory="generated_files"), name="files")

@app.post("/summarize/")
async def summarize_youtube(
    youtube_url: str = Form(...),
    output_type: str = Form("both"),
    language: str = Form("en"),
    file_type: str = Form("both")
):
    print(f"Output type selected: {output_type}")
    print(f"Language selected: {language}")

    # Extract video ID
    video_id = extract_video_id(youtube_url)

    # Step 1: Reuse transcript if cached
    transcript_path = f"transcripts/{video_id}_{language}.txt"
    transcript = None
    if os.path.exists(transcript_path):
        print("Transcript loaded from cache.")
        with open(transcript_path, "r") as f:
            transcript = f.read()
        _, metadata = download_audio(youtube_url)  # still get metadata
    else:
        # Download and transcribe
        audio_path, metadata = download_audio(youtube_url)
        transcript = transcribe_audio_with_cache(youtube_url, audio_path, language, metadata["duration"])

    # Step 2: Load or generate summary
    summary = None
    if output_type in ["summary", "both"]:
        summary = load_summary_from_cache(video_id, language)
        if not summary:
            summary = gpt_summary(transcript, language=language, thumbnail_url=metadata.get("thumbnail_url"))
            save_summary_to_cache(video_id, summary, language)

    # Step 3: Translate transcript if needed
    response = {}
    if output_type in ["transcript", "both"]:
        if language != "en":
            translated_transcript = translate_text(transcript, language)
            response["transcript"] = translated_transcript
        else:
            response["transcript"] = transcript
    if output_type in ["summary", "both"]:
        response["summary"] = summary

    # Step 4: Include metadata
    response["metadata"] = metadata

    # Step 5: Save files (txt/pdf)
    save_files(transcript, summary, output_type, file_type, save_dir="generated_files")

    # Step 6: Generate download links
    download_links = []
    if output_type in ["transcript", "both"]:
        if file_type in ["txt", "both"]:
            download_links.append("/files/transcript.txt")
        if file_type in ["pdf", "both"]:
            download_links.append("/files/transcript.pdf")
    if output_type in ["summary", "both"]:
        if file_type in ["txt", "both"]:
            download_links.append("/files/summary.txt")
        if file_type in ["pdf", "both"]:
            download_links.append("/files/summary.pdf")

    response["download_links"] = download_links

    log_request(
    video_id=video_id,
    duration=metadata.get("duration", 0),
    output_type=output_type,
    language=language,
    file_type=file_type,
    video_url=metadata.get("video_url", "N/A")
)

    return JSONResponse(content=response)
