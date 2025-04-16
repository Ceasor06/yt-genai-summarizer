import csv
import os
from datetime import datetime

LOG_FILE = "logs.csv"

# Ensure the log file exists with headers
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "timestamp", "video_id", "duration", "output_type", 
            "language", "file_type", "source_url"
        ])

def log_request(video_id: str, duration: int, output_type: str, language: str, file_type: str, video_url: str):
    timestamp = datetime.utcnow().isoformat()
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, video_id, duration, output_type, language, file_type, video_url])
