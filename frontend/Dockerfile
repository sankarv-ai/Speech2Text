# 1. Use official Python 3.10 slim image
FROM python:3.10.11

# 2. Set working directory
WORKDIR /app

# 3. Install system dependencies for audio + ffmpeg
RUN apt-get update && apt-get install -y \
    # ffmpeg \
    portaudio19-dev \
    # libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy requirements first (for caching)
COPY requirements.txt .

# 5. Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy app code including .streamlit folder
COPY . .

# 7. Expose Streamlit port
EXPOSE 8501

# 8. Run Streamlit app
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
