FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p assets/images assets/videos

ENV LOG_LEVEL=INFO
ENV POST_INTERVAL_HOURS=6
ENV MAX_POSTS_PER_DAY=4

ENTRYPOINT ["python", "main.py"]
CMD []
