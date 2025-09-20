# Import Required Libraries

import streamlit as st
import requests
import sounddevice as sd
import scipy.io.wavfile as wav
import tempfile



# FastAPI backend URL
FASTAPI_URL = "http://127.0.0.1:8080"  

# parameters
fs = 16000

st.title("AI-Powered Speech to Text App (FastAPI + Whisper + Streamlit + MySQL)")

# Record audio

st.header("Record Audio")
duration = st.number_input("Recording duration in (seconds):", min_value=1, max_value=30, value=5)


if st.button("Start Recording"):
    st.info("Recording started... Speak now ")

    # Record audio
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="int16")
    sd.wait()

    # Save to a temporary file (WAV format)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        wav.write(tmpfile.name, fs, recording)
        file_path = tmpfile.name

    st.success(f" Recording saved locally as {file_path}")

    # Upload to FastAPI
    with open(file_path, "rb") as f:
        files = {"file": ("recorded_audio.wav", f, "audio/wav")}
        try:
            response = requests.post(f"{FASTAPI_URL}/record", files=files, timeout=60)
            if response.status_code == 200:
                st.success("Uploaded successfully!")
                st.json(response.json())
            else:
                st.error(f"Upload failed: {response.status_code} {response.text}")
        except Exception as e:
            st.error(f"Connection error: {e}")


# Transcribe recording

st.header("Transcribe Audio")
if st.button("Transcribe Recording"):
    # Get latest recording from history
    history_response = requests.get(f"{FASTAPI_URL}/history")
    if history_response.status_code == 200 and history_response.json()["history"]:
        latest_record = history_response.json()["history"][0]  # newest first
        db_id = latest_record["id"]

        response = requests.post(f"{FASTAPI_URL}/transcribe", params={"db_id": db_id})
        if response.status_code == 200:
            result = response.json()
            st.success(" Transcription complete")
            st.write(result["transcription"])

            # Download option
            st.download_button(
                label="Download transcription",
                data=result["transcription"],
                file_name="transcription.txt",
                mime="text/plain"
            )
        else:
            st.error(" Transcription failed!")
    else:
        st.warning(" No recordings found to transcribe.")



# View transcription history

st.header("View Previous Transcriptions")
if st.button("Transcriptions History"):
    response = requests.get(f"{FASTAPI_URL}/history")
    if response.status_code == 200:
        history = response.json().get("history", [])
        if history:
            for record in history:
                with st.expander(f" {record['filename']} ({record['created_at']})"):
                    st.write("**Transcription:**")
                    st.write(record["transcription"])
                    st.write("**Audio File Path:**", record["audio_path"])

                    # Option to re-transcribe
                    if st.button(f"Re-transcribe {record['filename']}", key=f"re_{record['id']}"):
                        r = requests.post(f"{FASTAPI_URL}/transcribe", params={"db_id": record["id"]})
                        if r.status_code == 200:
                            new_result = r.json()
                            st.session_state[f"transcription_{record['id']}"] = new_result["transcription"]
                            st.session_state[f"status_{record['id']}"] = " Re-transcription complete"
                        else:
                            st.session_state[f"status_{record['id']}"] = " Re-transcription failed"

                    # Display status & transcription (if available in session state)
                    if f"status_{record['id']}" in st.session_state:
                        st.info(st.session_state[f"status_{record['id']}"])
                    if f"transcription_{record['id']}" in st.session_state:
                        st.write("**Latest Transcription:**")
                        st.write(st.session_state[f"transcription_{record['id']}"])
        else:
            st.info(" No transcriptions found in history.")
    else:
        st.error(" Failed to fetch history from FastAPI!")

