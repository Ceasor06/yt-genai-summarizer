# 🎥 GenAI YouTube Video Summarizer

This project is an AI-powered tool that takes a YouTube video URL, extracts the audio, transcribes it using OpenAI's Whisper, and summarizes the transcript using GPT. It's built with FastAPI and is containerized with Docker.

---

## 🚀 Features

- 🔊 Audio extraction from YouTube videos
- 🗣️ Transcription using OpenAI Whisper
- 🧠 Summarization using GPT-3.5/4 or open-source LLMs
- 📦 Docker-ready backend
- 💻 API-first architecture — ready for frontend or integration

---

## 📁 Project Structure

yt-summarizer/ ├── backend/ │ ├── app/ │ ├── requirements.txt │ └── Dockerfile ├── .env └── README.md

---

## 🛠️ Getting Started

### 1. Clone the Repo
```bash
git clone https://github.com/your-username/yt-summarizer.git
cd yt-summarizer

### 2. Set up Virtual Environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

### 3. Install Dependencies
pip install -r backend/requirements.txt

### 4. Add OpenAI API Key
#Create a .env file in the root:

OPENAI_API_KEY=your_openai_key

### 5. Run the API
uvicorn app.main:app --reload