import urllib.request
import urllib.error
import json
import logging
import asyncio
import google.genai as genai

from config.api_keys import GEMINI_API_KEY

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

gemini_client = genai.Client(api_key=GEMINI_API_KEY)

def _speech_config_from_mime_type(mime_type: str) -> dict:
    encoding_map = {
        "audio/webm": "WEBM_OPUS",
        "audio/ogg": "OGG_OPUS",
        "audio/flac": "FLAC",
        "audio/wav": "LINEAR16",
        "audio/x-wav": "LINEAR16",
        "audio/mp3": "MP3",
        "audio/mpeg": "MP3",
    }
    sample_rate_map = {
        "audio/webm": 48000,
        "audio/ogg": 48000,
        "audio/wav": 16000,
        "audio/x-wav": 16000,
        "audio/flac": 16000,
    }
    encoding = encoding_map.get(mime_type, "WEBM_OPUS")
    config = {
        "encoding": encoding,
        "languageCode": "en-US",
        "enableAutomaticPunctuation": True,
        "model": "latest_long",
    }
    sample_rate = sample_rate_map.get(mime_type)
    if sample_rate:
        # noinspection PyTypeChecker
        config["sampleRateHertz"] = sample_rate
    return config


def _google_speech_post(url: str, payload: dict) -> dict:
    request_data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=request_data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def _google_speech_get(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def _extract_transcript(response: dict) -> str:
    parts = []
    for result in response.get("results", []):
        alternatives = result.get("alternatives") or []
        if alternatives:
            transcript = alternatives[0].get("transcript", "").strip()
            if transcript:
                parts.append(transcript)
    return " ".join(parts).strip()


async def transcribe_audio_with_gemini(audio: bytes, mime_type: str = "audio/mp3") -> str:
    """
    Transcribes audio using Gemini 2.5 Flash.
    """
    logger.info("[Transcription] Starting Gemini transcription...")

    # Create audio part from bytes
    audio_part = genai.types.Part.from_bytes(
        data=audio,
        mime_type=mime_type,
    )

    prompt_text = "Transcribe this audio file exactly as spoken."

    # Run sync Gemini call in thread pool to maintain async compatibility
    response = await asyncio.to_thread(
        gemini_client.models.generate_content,
        model="gemini-2.5-flash",
        contents=[audio_part, prompt_text],
    )

    logger.info(f"[Transcription] Complete ({len(response.text)} characters)")
    return response.text