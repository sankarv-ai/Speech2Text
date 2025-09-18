# AI-Powered Speech-to-Text App (FastAPI + Whisper + Streamlit + MySQL)

## Project Overview
This project is an **end-to-end Speech-to-Text application** that records audio from a user, transcribes it using **OpenAI Whisper**, and stores the results in a **MySQL database**.  
It combines a **FastAPI backend** for recording/transcription with a **Streamlit frontend** for user interaction and database history viewing.  

---

## Features
- Record audio directly from your microphone  
- Transcribe audio using **Whisper (OpenAI)**  
- Store recordings path & transcriptions in **MySQL**  
- View transcription history with timestamps  
- Re-transcribe old recordings anytime  
- Download transcription as a text file  

---

## Tech Stack
- **Frontend:** Streamlit  
- **Backend:** FastAPI  
- **ASR Model:** Whisper (OpenAI)  
- **Database:** MySQL (SQLAlchemy ORM)  
- **Audio Processing:** SoundDevice, Librosa, Scipy  

---

## Installation & Setup

### 1 Clone Repository
```bash
git clone https://github.com/your-username/speech-to-text-app.git
cd speech-to-text-app
```

### 2 Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

### 3 Install Requirements
```bash
pip install -r requirements.txt
```

### 4 Configure MySQL
Start MySQL server
Create a database (example: transcriptions_db):
```bash
mysql -u root -p
CREATE DATABASE transcriptions_db;

# Update DATABASE_URL in main.py:
DATABASE_URL = "mysql+pymysql://root:yourpassword@localhost/transcriptions_db"
```
### 5 Run FastAPI Backend
```bash
cd backend
uvicorn main:app --reload --port 8080
```

### 6 Run Streamlit Frontend
```bash
cd frontend
streamlit run app.py
```

### Database Schema

Table: transcriptions

| Column        | Type     | Description                       |
| ------------- | -------- | --------------------------------- |
| id            | INT (PK) | Auto-incremented unique ID        |
| filename      | VARCHAR  | Saved audio file name             |
| audio\_path   | VARCHAR  | Path to stored audio file         |
| transcription | TEXT     | Transcribed text                  |
| created\_at   | DATETIME | Timestamp when record was created |




