import os
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

load_dotenv()

# Load credentials
SPEECH_KEY = os.getenv("AZURE_TTS_KEY")
SPEECH_REGION = os.getenv("AZURE_TTS_REGION")
VOICE = os.getenv("AZURE_TTS_VOICE", "en-US-AriaNeural")  # fallback voice

def synthesize_speech(text: str, output_path: str = "output.wav") -> str:
    """
    Converts text to speech and saves audio file.
    Returns the file path.
    """
    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
    speech_config.speech_synthesis_voice_name = VOICE

    audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path)

    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    result = synthesizer.speak_text_async(text).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f"✅ Speech synthesized and saved to {output_path}")
        return output_path
    else:
        raise Exception(f"TTS failed: {result.reason}")
