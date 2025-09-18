# Import Required Libraries

import streamlit as st
import requests

# FastAPI backend URL
FASTAPI_URL = "http://127.0.0.1:8080"  

st.title("AI-Powered Speech to Text App (FastAPI + Whisper + Streamlit)")



# Record audio

st.header("Record Audio")
duration = st.number_input("Recording duration in (seconds):", min_value=1, max_value=30, value=5)

if st.button("Start Recording"):
    response = requests.post(f"{FASTAPI_URL}/record", params={"duration": duration})
    if response.status_code == 200:
        data = response.json()
        st.success(f" Audio recorded: {data['filename']} (DB ID: {data['db_id']})")
    else:
        st.error("Recording failed!")



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
