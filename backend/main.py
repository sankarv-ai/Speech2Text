# Imports required Libraries

from fastapi import FastAPI, Query, Depends, UploadFile, File
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, func
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from fastapi.responses import JSONResponse
from typing import Optional
import whisper
import librosa
import os
import uuid
import pymysql

# Database setup (MySQL)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "database_url"
)


engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Transcription(Base):
    __tablename__ = "transcriptions"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    audio_path = Column(String(255))          
    transcription = Column(Text, nullable=False)         
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Create table if not exists
Base.metadata.create_all(bind=engine)


# FastAPI + Whisper

app = FastAPI()

@app.get("/")
def root():
    return {"message": "FastAPI is running"}

# Load Whisper model once
model = whisper.load_model("small")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Record audio

@app.post("/record")
async def record_audio(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Record audio from system microphone and save as WAV file with a unique name.
    """
    try:
        # Generate unique filename
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{unique_id}{file.filename}"

        # Ensure uploads directory exists
        os.makedirs("uploads", exist_ok=True)
        file_path = os.path.join("uploads", filename)

        # Save uploaded file to disk
        with open(file_path, "wb") as f:
            f.write(await file.read())
       
        # Save entry in DB 
        db_entry = Transcription(
            filename=filename,
            audio_path=file_path,
            transcription=""
        )
        db.add(db_entry)
        db.commit()
        db.refresh(db_entry)

        return {
            "status": "success",
            "filename": filename,
            "audio_path":file_path,
            "db_id": db_entry.id,
            "message": f"Recording saved to {file_path}"
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


# Transcribe audio

@app.post("/transcribe")
async def transcribe_audio(
    db_id: Optional[int] = Query(None, description="Database ID of the recording"),
    input_audio_path: Optional[str] = Query(None, description="Path to input WAV file"),
    db: Session = Depends(get_db)
):
    """
    Transcribe audio using Whisper. You can pass either db_id or file path.
    Saves transcription both to text file and SQLite DB.
    """
    try:
        # If db_id provided, fetch file from DB
        if db_id is not None:
            record = db.query(Transcription).filter(Transcription.id == db_id).first()
            if not record:
                return {"status": "error", "message": f"No record found with id {db_id}"}
            input_audio_path = record.audio_path

        if not input_audio_path or not os.path.exists(input_audio_path):
            return {"status": "error", "message": "Invalid or missing audio file"}

        # Load and resample audio to 16 kHz
        audio, sr = librosa.load(input_audio_path, sr=16000)

        # Transcribe audio
        result = model.transcribe(audio, language="en")
        transcription = result["text"]

        # Save transcription to a text file
        output_file = f"{os.path.splitext(input_audio_path)[0]}_transcription.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(transcription)

        # Update DB entry
        record = db.query(Transcription).filter(Transcription.audio_path == input_audio_path).first()
        if record:
            record.transcription = transcription
            db.commit()
            db.refresh(record)

        return {
            "status": "success",
            "input_file": input_audio_path,
            "transcription_file": output_file,
            "transcription": transcription,
            "db_id": record.id if record else None
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


# Get history

@app.get("/history")
async def get_history(db: Session = Depends(get_db)):
    try:
        records = db.query(Transcription).order_by(Transcription.created_at.desc()).all()
        data = [
            {
                "id": r.id,
                "filename": r.filename,
                "audio_path": r.audio_path,
                "transcription": r.transcription,
                "created_at": str(r.created_at)
            }
            for r in records
        ]
        return {"status": "success", "history": data}
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)
