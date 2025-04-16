import whisper

model = whisper.load_model("base")  # You can use "small" or "medium" if you want

def transcribe_audio(file_path: str) -> str:
    result = model.transcribe(file_path)
    return result["text"]
w