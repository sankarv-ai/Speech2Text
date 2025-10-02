from fastapi import FastAPI, WebSocket
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
from aiortc.contrib.media import MediaBlackhole
import whisper
import numpy as np
import asyncio

app = FastAPI()
print("for fastAPI class the instance will be created called app")


# Load Whisper model once
model = whisper.load_model("base")
print("The Whisper model will be loaded into variable called model")
# ----------------------------
# WebSocket for transcription push
# ----------------------------
clients = set()

@app.websocket("/ws/transcription")
async def transcription_ws(websocket: WebSocket):
    await websocket.accept()
    print("The websocket connection will be accepted by the server side")
    clients.add(websocket)
    print("The new client will be added to the clients set")

    try:
        while True:
            await asyncio.sleep(1)
    except Exception:
        pass
    finally:
        clients.remove(websocket)
        print("users will be reoved from the clients set")

async def broadcast_transcription(text: str):
    for ws in clients:
        try:
            await ws.send_text(text)
            print("the transcription will be sent to the client side")
        except Exception:
            pass

# ----------------------------
# WebRTC Handling
# ----------------------------
class AudioTrack(MediaStreamTrack):
    kind = "audio"
    print("The input Audio is audio only format")

    def __init__(self, track):
        super().__init__()
        self.track = track

    async def recv(self):
        frame = await self.track.recv()
        print("the input Audio data will looks like",)
        # Convert audio frame to numpy PCM
        pcm = frame.to_ndarray().astype(np.float32) / 32768.0
        print("The Audio data will be converted into numpy array")
        # Run Whisper transcription
        result = model.transcribe(pcm, fp16=False, language="en")
        print("the model will get the input and provide the transcription")
        text = result["text"].strip()
        print("the transcription will stored at the text variable")
        # Broadcast transcription to WebSocket clients
        asyncio.create_task(broadcast_transcription(text))
        print("the transcription will be broadcast to the websocket clients")
        return frame  # forward frame

pcs = set()

@app.post("/offer")
async def offer(sdp: dict):
    print("The sdp offer will be received by server side")
    pc = RTCPeerConnection()
    print("the webRTC connection will be established")
    pcs.add(pc)

    @pc.on("track")
    def on_track(track):
        print("The Audio data will enter into the server side")
        if track.kind == "audio":
            pc.addTrack(AudioTrack(track))
        else:
            pc.addTrack(MediaBlackhole())

    offer = RTCSessionDescription(sdp["sdp"], sdp["type"])
    await pc.setRemoteDescription(offer)

    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
