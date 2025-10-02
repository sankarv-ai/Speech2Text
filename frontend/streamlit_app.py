import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import asyncio
import websockets
import threading

st.title("Real-time Speech Transcription (WebRTC + Whisper)")

# ----------------------------
# WebRTC Config
webrtc_ctx = webrtc_streamer(
    key="speech-demo",
    mode=WebRtcMode.SENDONLY,
    media_stream_constraints={"audio": True, "video": False},
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
    async_processing=True  # makes sure frames are processed

)

# ----------------------------
# WebSocket Listener for Transcriptions
transcription_placeholder = st.empty()
transcription_text = ""

async def listen_transcriptions():
    global transcription_text
    uri = "ws://127.0.0.1:8080/ws/transcription"
    try:
        async with websockets.connect(uri, ping_interval=None) as ws:
            while True:
                text = await ws.recv()
                transcription_text += " " + text
                transcription_placeholder.text_area("Live Transcription:", transcription_text, height=200)
    except Exception as e:
        st.error(f"WebSocket error: {e}")

def start_ws_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(listen_transcriptions())

# Start WebSocket listener only if WebRTC is playing
if webrtc_ctx.state.playing:
    st.info("🎤 Streaming audio via WebRTC...")
    threading.Thread(target=start_ws_loop, daemon=True).start()
