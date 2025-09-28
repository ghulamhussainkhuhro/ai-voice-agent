from fastapi import FastAPI, UploadFile, File
from backend import stt, llm, tts
from fastapi.responses import FileResponse
import tempfile

app = FastAPI()

@app.get("/")
def root():
    return {"message": "AI Voice Agent backend is running 🚀"}

@app.post("/stt")
async def speech_to_text(file: UploadFile = File(...)):
    """
    Accepts an audio file, returns transcribed text.
    """
    # Save uploaded audio temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        temp_audio.write(await file.read())
        temp_path = temp_audio.name

    # Run transcription
    transcript = stt.transcribe_audio(temp_path)
    return {"transcript": transcript}

# ---------- Text to LLM Response ----------
@app.post("/chat")
def chat_with_llm(payload: dict):
    """
    Accepts user text, returns LLM response.
    """
    user_text = payload.get("text", "")
    if not user_text:
        return {"error": "No text provided"}
    response = llm.ask_llm(user_text)
    return {"response": response}

# uvicorn backend.app:app --reload


@app.post("/tts")
def text_to_speech(payload: dict):
    text = payload.get("text", "")
    if not text:
        return {"error": "No text provided"}
    
    # Save audio to temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        output_path = temp_audio.name

    audio_file = tts.synthesize_speech(text, output_path)
    return FileResponse(audio_file, media_type="audio/wav", filename="response.wav")