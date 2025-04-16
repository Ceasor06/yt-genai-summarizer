import gradio as gr
import requests

# Define your backend URL (adjust if hosted elsewhere)
BACKEND_URL = "http://127.0.0.1:8000/summarize/"

def summarize_video(youtube_url, output_type, language, file_type):
    # Prepare form data
    data = {
        'youtube_url': youtube_url,
        'output_type': output_type,
        'language': language,
        'file_type': file_type
    }

    # Send POST request
    try:
        response = requests.post(BACKEND_URL, data=data)
        response.raise_for_status()
        result = response.json()

        # Extract response
        transcript = result.get("transcript", "")
        summary = result.get("summary", "")
        metadata = result.get("metadata", {})
        links = result.get("download_links", [])
        

        # 📄 Build display output
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
                full_url = f"http://127.0.0.1:8000{link}"
                display += f"- [{filename}]({full_url})\n"

        return display

    except Exception as e:
        return f"❌ Error: {e}"


# Gradio UI
iface = gr.Interface(
    fn=summarize_video,
    inputs=[
        gr.Textbox(label="YouTube URL", placeholder="Paste YouTube video link here"),
        gr.Radio(["transcript", "summary", "both"], label="Select Output Type", value="both"),
        gr.Textbox(label="Language (e.g., en, hi, fr)", value="en"),
        gr.Radio(["txt", "pdf", "both"], label="Download Format", value="both"),
    ],
    outputs=gr.Markdown(),
    title="YouTube GenAI Summarizer",
    description="Upload a YouTube video and get transcript/summary powered by Whisper + Gemini",
)

if __name__ == "__main__":
    iface.launch()


# import gradio as gr
# import requests

# BACKEND_URL = "http://127.0.0.1:8000/summarize/"

# def summarize_video(youtube_url, output_type, language, file_type):
#     status = "⏳ Processing... Please wait."
#     try:
#         # Prepare form data
#         data = {
#             'youtube_url': youtube_url,
#             'output_type': output_type,
#             'language': language,
#             'file_type': file_type
#         }

#         response = requests.post(BACKEND_URL, data=data)
#         response.raise_for_status()
#         result = response.json()

#         # Extract response
#         transcript = result.get("transcript", "")
#         summary = result.get("summary", "")
#         metadata = result.get("metadata", {})
#         detected_language = result.get("detected_language", "Unknown")
#         links = result.get("download_links", [])

#         display = f"🎬 **Video Title:** {metadata.get('title', 'N/A')}\n"
#         display += f"📅 **Upload Date:** {metadata.get('upload_date', 'N/A')}\n"
#         display += f"👤 **Uploader:** {metadata.get('uploader', 'N/A')}\n"
#         display += f"⏱️ **Duration:** {metadata.get('duration', 'N/A')} seconds\n"
#         display += f"📊 **Views:** {metadata.get('view_count', 'N/A')}\n"
#         display += f"👍 **Likes:** {metadata.get('like_count', 'N/A')}\n"
#         display += f"🌐 **Detected Language:** {detected_language}\n"
#         display += f"🔗 [Watch on YouTube]({metadata.get('video_url', '#')})\n\n"
#         thumbnail = metadata.get("thumbnail_url")
#         if thumbnail:
#             display += f"[![Thumbnail]({thumbnail})]({metadata.get('video_url', '#')})\n\n"

#         if transcript:
#             display += f"## 📝 Transcript:\n{transcript}\n\n"
#         if summary:
#             display += f"## ✨ Summary:\n{summary}\n\n"

#         if links:
#             display += "## 📥 Download Files:\n"
#             for link in links:
#                 filename = link.split("/")[-1]
#                 full_url = f"http://127.0.0.1:8000{link}"
#                 display += f"- [{filename}]({full_url})\n"

#         status = "✅ Done!"
#         return display, status

#     except Exception as e:
#         return f"❌ Error: {e}", "⚠️ Failed."

# # Gradio UI
# with gr.Blocks() as iface:
#     gr.Markdown("🎧 **YouTube GenAI Summarizer**")
#     with gr.Row():
#         youtube_url = gr.Textbox(label="YouTube URL")
#     with gr.Row():
#         output_type = gr.Radio(["transcript", "summary", "both"], label="Select Output", value="both")
#         file_type = gr.Radio(["txt", "pdf", "both"], label="Download Format", value="both")
#         language = gr.Textbox(label="Language (e.g., en, hi, fr)", value="en")
#     submit_btn = gr.Button("Summarize")
#     status = gr.Textbox(label="Status", interactive=False, value="", visible=True)
#     result_output = gr.Markdown()

#     submit_btn.click(
#         summarize_video,
#         inputs=[youtube_url, output_type, language, file_type],
#         outputs=[result_output, status]
#     )

# if __name__ == "__main__":
#     iface.launch()