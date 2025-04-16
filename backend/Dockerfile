FROM python:3.9-slim

WORKDIR /app

COPY ./requirements.txt /app/
RUN apt-get update && apt-get install -y ffmpeg
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY ./app /app/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
