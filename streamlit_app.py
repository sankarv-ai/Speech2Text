import streamlit as st
import asyncio
import websockets
import sounddevice as sd
import numpy as np

st.title("Real-time Speech Transcription (WebSocket + Whisper)")

FS = 16000  # Sample rate
DURATION = 5  # seconds per chunk

async def record_and_stream():
    uri = "ws://127.0.0.1:8090/ws/audio"
    try:
        async with websockets.connect(uri, ping_interval=None) as ws:
            st.info("Recording... Speak now ")

            # One placeholder for live transcription
            transcription_placeholder = st.empty()
            transcription_text = ""  # store cumulative text

            while True:
                # Record chunk
                recording = sd.rec(int(DURATION * FS), samplerate=FS, channels=1, dtype="int16")
                sd.wait()
                print("The Audio Data will looks like :",recording)
                # Convert to bytes
                chunk_bytes = recording.tobytes()
                # print("the chunk bytes will be looks like ",chunk_bytes)

                # Send chunk to FastAPI
                await ws.send(chunk_bytes)
                # print("Chunk sent to backend")

                # Wait for transcription response
                result = await ws.recv()
                # print("Transcription received from backend")
                # print("the transcriptions is :",result)

                # Update cumulative transcription
                transcription_text += " " + result.strip()
                # print("the received text join with existing text")
                # print("the joined text will be ",transcription_text)

                # Update the placeholder instead of re-creating widget
                transcription_placeholder.text_area(
                    "Live Transcription:",
                    transcription_text,
                    height=200
                )
                # print("text added to text_area")
    except websockets.exceptions.ConnectionClosedOK:
        st.warning("WebSocket closed normally.")
    except websockets.exceptions.ConnectionClosedError as e:
        st.error(f"WebSocket closed with error: {e}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")

if st.button("Start Recording"):
    asyncio.run(record_and_stream())
