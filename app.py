import os
from dotenv import load_dotenv
from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import gradio as gr
import requests

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

load_dotenv()

# ------------------ FASTAPI BACKEND ------------------

app = FastAPI()
app.mount("/files", StaticFiles(directory="generated_files"), name="files")

@app.post("/summarize/")
async def summarize_youtube(
    youtube_url: str = Form(...),
    output_type: str = Form("both"),
    language: str = Form("en"),
    file_type: str = Form("both")
):
    video_id = extract_video_id(youtube_url)

    transcript_path = f"transcripts/{video_id}_{language}.txt"
    transcript = None
    detected_lang = "en"
    if os.path.exists(transcript_path):
        print("Transcript loaded from cache.")
        with open(transcript_path, "r") as f:
            transcript = f.read()
        _, metadata = download_audio(youtube_url)
    else:
        audio_path, metadata = download_audio(youtube_url)
        transcript = ""
        transcript = transcribe_audio_with_cache(
            youtube_url, audio_path, language, metadata["duration"]
        )

    summary = None
    if output_type in ["summary", "both"]:
        summary = load_summary_from_cache(video_id, language)
        if not summary:
            summary = gpt_summary(transcript, language=language, thumbnail_url=metadata.get("thumbnail_url"))
            save_summary_to_cache(video_id, summary, language)

    response = {}
    if output_type in ["transcript", "both"]:
        if language != "en":
            translated_transcript = translate_text(transcript, language)
            response["transcript"] = translated_transcript
        else:
            response["transcript"] = transcript
    if output_type in ["summary", "both"]:
        response["summary"] = summary

    response["metadata"] = metadata
    save_files(transcript, summary, output_type, file_type, save_dir="generated_files")

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
    return JSONResponse(content=response)

# ------------------ GRADIO FRONTEND ------------------

def summarize_video_gradio(youtube_url, output_type, language, file_type):
    data = {
        'youtube_url': youtube_url,
        'output_type': output_type,
        'language': language,
        'file_type': file_type
    }

    try:
        response = requests.post("http://localhost:7860/summarize/", data=data)
        result = response.json()

        transcript = result.get("transcript", "")
        summary = result.get("summary", "")
        metadata = result.get("metadata", {})
        links = result.get("download_links", [])

        display = f"🎬 **Video Title:** {metadata.get('title', 'N/A')}\n"
        display += f"📅 **Upload Date:** {metadata.get('upload_date', 'N/A')}\n"
        display += f"👤 **Uploader:** {metadata.get('uploader', 'N/A')}\n"
        display += f"⏱️ **Duration:** {metadata.get('duration', 'N/A')} seconds\n"
        display += f"📊 **Views:** {metadata.get('view_count', 'N/A')}\n"
        display += f"👍 **Likes:** {metadata.get('like_count', 'N/A')}\n"
        display += f"🔗 [Watch on YouTube]({metadata.get('video_url', '#')})\n\n"

        thumbnail = metadata.get("thumbnail_url")
        if thumbnail:
            display += f"[![Thumbnail]({thumbnail})]({metadata.get('video_url', '#')})\n\n"

        if transcript:
            display += f"## 📝 Transcript:\n{transcript}\n\n"
        if summary:
            display += f"## ✨ Summary:\n{summary}\n\n"

        if links:
            display += "## 📥 Download Files:\n"
            for link in links:
                filename = link.split("/")[-1]
                full_url = f"/files/{filename}"
                display += f"- [{filename}]({full_url})\n"

        return display
    except Exception as e:
        return f"❌ Error: {e}"

gradio_app = gr.Interface(
    fn=summarize_video_gradio,
    inputs=[
        gr.Textbox(label="YouTube URL", placeholder="Paste YouTube video link here"),
        gr.Radio(["transcript", "summary", "both"], label="Select Output Type", value="both"),
        gr.Textbox(label="Language (e.g., en, hi, fr)", value="en"),
        gr.Radio(["txt", "pdf", "both"], label="Download Format", value="both"),
    ],
    outputs=gr.Markdown(),
    title="🎧 YouTube GenAI Summarizer",
    description="Upload a YouTube video and get transcript/summary powered by Whisper + Gemini",
)

app = gr.mount_gradio_app(app, gradio_app, path="/")
