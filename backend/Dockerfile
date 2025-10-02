# 1. Use official Python 3.10 slim image
FROM python:3.10.11

# 2. Set working directory
WORKDIR /app

# # 3. Install system dependencies for Whisper + audio
# RUN apt-get update && apt-get install -y \
#     ffmpeg \
#     build-essential \
#     git \
#     && rm -rf /var/lib/apt/lists/*

# 4. Copy requirements first (for caching)
COPY requirements.txt .

# 5. Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 6. Pre-download Whisper small model
RUN python -c "import whisper; whisper.load_model('tiny')"

# 7. Copy backend code
COPY . .

# 8. Expose FastAPI port
EXPOSE 8070

# 9. Run FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8070"]
