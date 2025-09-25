from fastapi import FastAPI, WebSocket
import numpy as np
import whisper

app = FastAPI()

# Load Whisper model once
model = whisper.load_model("base")

@app.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            # Receive one audio chunk from frontend
            data = await websocket.receive_bytes()
            print("Received audio chunk from frontend")

            # Convert raw bytes -> numpy array -> normalize
            audio = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0

            # Run Whisper directly on chunk (no temp file needed)
            result = model.transcribe(audio, fp16=False, language='en')
            text = result["text"].strip()
            print("Transcribed chunk:", text)

            # Send transcription back
            await websocket.send_text(text)
            print("Transcription send to frontend")

    except Exception as e:
        print("WebSocket closed:", e)
    finally:
        await websocket.close()
