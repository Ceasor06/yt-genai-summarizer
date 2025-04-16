from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai
import os
from typing import List
from fpdf import FPDF
import tiktoken
import requests
from PIL import Image
from io import BytesIO

api_key = os.getenv("GOOGLE_API_KEY")
text_model = genai.GenerativeModel("models/gemini-1.5-pro-002")
vision_model = genai.GenerativeModel("models/gemini-pro-vision")

MAX_CHARS = 8000

# -------------------- TEXT CHUNKING --------------------
def chunk_text(text: str, chunk_size: int = MAX_CHARS) -> List[str]:
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")  # Approximate tokenizer
    tokens = encoding.encode(text)
    return [encoding.decode(tokens[i:i + chunk_size]) for i in range(0, len(tokens), chunk_size)]

# -------------------- TRANSLATE TEXT --------------------
def translate_text(text: str, language: str) -> str:
    prompt = f"Translate the following transcript into {language}:\n\n{text}"
    response = text_model.generate_content(prompt)
    return response.text

# -------------------- THUMBNAIL ANALYSIS --------------------
def analyze_thumbnail(thumbnail_url: str) -> str:
    try:
        response = requests.get(thumbnail_url)
        image = Image.open(BytesIO(response.content))

        prompt = "Analyze this YouTube thumbnail and describe what you observe. Mention any text, people, emotions, or key visual themes."

        vision_response = vision_model.generate_content([prompt, image])
        return vision_response.text
    except Exception as e:
        print("Thumbnail analysis failed:", e)
        return ""

# -------------------- SUMMARIZATION --------------------
def gpt_summary(text: str, language: str = "en", thumbnail_url: str = None) -> str:
    if language != "en":
        text = translate_text(text, language)

    chunks = chunk_text(text)
    partial_summaries = []

    for idx, chunk in enumerate(chunks):
        prompt = f"Summarize the following YouTube transcript chunk ({idx+1}/{len(chunks)}) in {language}:\n\n{chunk}"
        response = text_model.generate_content(prompt)
        partial_summaries.append(response.text)

        joined_summaries = "\n\n".join(partial_summaries)
        final_prompt = (
            f"Combine and polish the following summaries into a coherent final summary in {language}:\n\n"
            f"{joined_summaries}\n\n"
            "After the summary, provide 5-7 concise key points (in bullet format) that highlight the most important insights or takeaways from the video."
        )

    # If thumbnail is available, integrate visual context
    if thumbnail_url:
        thumbnail_analysis = analyze_thumbnail(thumbnail_url)
        final_prompt += f"\n\nAlso include insights based on this thumbnail analysis:\n{thumbnail_analysis}"

    final_response = text_model.generate_content(final_prompt)
    return final_response.text


# -------------------- FILE SAVING --------------------
def save_files(transcript: str, summary: str, output_type: str, file_type: str, save_dir: str = "generated_files"):
    os.makedirs(save_dir, exist_ok=True)

    def write_txt(filename: str, content: str):
        with open(os.path.join(save_dir, filename), "w", encoding="utf-8") as f:
            f.write(content)

    def write_pdf(filename: str, content: str):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_font("DejaVu", "", "fonts/DejaVuSans.ttf", uni=True)
        pdf.set_font("DejaVu", size=12)
        for line in content.split('\n'):
            pdf.multi_cell(0, 10, txt=line)
        pdf.output(os.path.join(save_dir, filename))

    if output_type in ["transcript", "both"]:
        if file_type in ["txt", "both"]:
            write_txt("transcript.txt", transcript)
        if file_type in ["pdf", "both"]:
            write_pdf("transcript.pdf", transcript)

    if summary and output_type in ["summary", "both"]:
        if file_type in ["txt", "both"]:
            write_txt("summary.txt", summary)
        if file_type in ["pdf", "both"]:
            write_pdf("summary.pdf", summary)

# -------------------- CACHE HANDLING --------------------
def load_summary_from_cache(video_id: str, language: str, cache_dir="summaries") -> str | None:
    os.makedirs(cache_dir, exist_ok=True)
    cache_path = os.path.join(cache_dir, f"{video_id}_{language}.txt")
    if os.path.exists(cache_path):
        print("Summary loaded from cache.")
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()
    return None

def save_summary_to_cache(video_id: str, summary: str, language: str, cache_dir="summaries"):
    os.makedirs(cache_dir, exist_ok=True)
    cache_path = os.path.join(cache_dir, f"{video_id}_{language}.txt")
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(summary)
