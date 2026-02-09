from elevenlabs.client import ElevenLabs
from config.api_keys import ELEVENLABS_API_KEY


def generate_speech(text: str) -> bytes:
    """
    Generate speech audio from text using ElevenLabs API.

    Args:
        text: The text to convert to speech

    Returns:
        Audio bytes in MP3 format
    """
    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

    audio_generator = client.text_to_speech.convert(
        voice_id="TX3LPaxmHKxFdv7VOQHJ",
        text=text,
        model_id="eleven_multilingual_v2",
    )

    # Convert generator to bytes
    audio_bytes = b"".join(audio_generator)
    return audio_bytes