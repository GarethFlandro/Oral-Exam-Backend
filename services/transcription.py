import time
import urllib.request
import urllib.error
import json
import logging
import asyncio
import base64

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

from config.api_keys import GEMINI_API_KEY

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


async def transcribe_audio_with_google_speech_api_key(
    audio: bytes,
    mime_type: str = "audio/webm",
    language_code: str = "en-US",
    timeout_seconds: int = 600,
) -> str:
    """
    Transcribe audio using Google Speech-to-Text REST API with the Gemini API key.
    """
    logger.info("[Transcription] Starting audio transcription with Google Speech-to-Text...")
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is required for Google Speech-to-Text.")

    audio_base64 = base64.standard_b64encode(audio).decode("utf-8")
    config = _speech_config_from_mime_type(mime_type)
    config["languageCode"] = language_code

    payload = {
        "config": config,
        "audio": {"content": audio_base64},
    }

    start_url = (
        "https://speech.googleapis.com/v1/speech:longrunningrecognize?key="
        f"{GEMINI_API_KEY}"
    )
    logger.info("[Transcription] Sending audio to Google Speech-to-Text API...")
    start_response = await asyncio.to_thread(_google_speech_post, start_url, payload)
    operation_name = start_response.get("name")
    if not operation_name:
        raise RuntimeError("Google Speech-to-Text did not return an operation name.")

    poll_url = (
        "https://speech.googleapis.com/v1/operations/"
        f"{operation_name}?key={GEMINI_API_KEY}"
    )
    deadline = time.time() + timeout_seconds
    logger.info("[Transcription] Waiting for transcription to complete...")

    while time.time() < deadline:
        operation = await asyncio.to_thread(_google_speech_get, poll_url)
        if operation.get("done"):
            if "error" in operation:
                message = operation["error"].get("message", "Unknown error")
                logger.error(f"[Transcription] FAILED: {message}")
                raise RuntimeError(f"Google Speech-to-Text failed: {message}")
            response = operation.get("response", {})
            transcript = _extract_transcript(response)
            logger.info(f"[Transcription] Complete ({len(transcript)} characters)")
            return transcript
        time.sleep(2)

    raise TimeoutError("Google Speech-to-Text timed out waiting for transcription.")