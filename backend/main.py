# backend/main.py
"""
Main FastAPI app for voice-to-voice conversation.
Supports:
  - HTTP endpoint (/converse)
  - WebSocket endpoint (/ws/converse) for turn-based voice chat
"""

import os
import uuid
import tempfile
from fastapi import FastAPI, UploadFile, File, WebSocket
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from backend import stt, llm, tts

app = FastAPI()

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ allow all for dev; restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")


# ---------- Converse (HTTP) ----------
@app.post("/converse")
async def converse(file: UploadFile = File(...)):
    """HTTP endpoint for voice → voice pipeline."""
    try:
        # --- Save uploaded audio ---
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(await file.read())
            input_audio_path = temp_audio.name

        return process_conversation(input_audio_path)

    except Exception as e:
        return JSONResponse({"error": f"Unexpected server error: {e}"}, status_code=500)


# ---------- Converse (WebSocket) ----------
@app.websocket("/ws/converse")
async def websocket_converse(ws: WebSocket):
    """WebSocket endpoint for voice → voice pipeline."""
    await ws.accept()
    try:
        while True:
            data = await ws.receive_bytes()  # receive audio as bytes

            # --- Save incoming audio chunk ---
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
                temp_audio.write(data)
                input_audio_path = temp_audio.name

            result = process_conversation(input_audio_path)
            await ws.send_json(result)

    except Exception as e:
        await ws.send_json({"error": f"WebSocket error: {e}"})
    finally:
        await ws.close()


# ---------- Core pipeline ----------
def process_conversation(input_audio_path: str) -> dict:
    """Shared pipeline for STT → LLM → TTS."""
    # --- STT ---
    transcript = stt.transcribe_audio(input_audio_path)
    if not transcript or transcript.startswith("[STT Error"):
        return {"error": "Speech-to-text failed", "details": transcript}

    # --- LLM ---
    llm_response = llm.ask_llm(transcript)
    if not llm_response or llm_response.startswith("[Error"):
        return {"error": "LLM failed", "details": llm_response}

    # --- TTS ---
    unique_name = f"{uuid.uuid4().hex}.wav"
    output_path = os.path.join(tempfile.gettempdir(), unique_name)
    tts_result = tts.synthesize_speech(llm_response, output_path)

    if not os.path.exists(tts_result):
        return {"error": "Text-to-speech failed", "details": tts_result}

    return {
        "transcript": transcript,
        "response": llm_response,
        "audio_file": f"{BACKEND_URL}/download/{unique_name}",
    }


# ---------- Download generated audio ----------
@app.get("/download/{filename}")
def download_file(filename: str):
    """Return TTS audio for playback."""
    file_path = os.path.join(tempfile.gettempdir(), filename)

    if not os.path.exists(file_path):
        return JSONResponse({"error": "File not found."}, status_code=404)

    return FileResponse(file_path, media_type="audio/wav", filename=filename)
