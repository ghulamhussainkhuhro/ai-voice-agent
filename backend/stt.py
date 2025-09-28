import whisper
from pathlib import Path

# Load Whisper model once (tiny = fast, base = better, small/medium/large = heavier)
model = whisper.load_model("base")

def transcribe_audio(file_path: str) -> str:
    """
    Transcribe audio file to text using Whisper.
    Args:
        file_path (str): path to audio file (.wav, .mp3, etc.)
    Returns:
        str: transcribed text
    """
    result = model.transcribe(file_path)
    return result["text"].strip()
