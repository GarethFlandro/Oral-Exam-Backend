import json
from dataclasses import dataclass
import google.genai as genai
import logging
import asyncio

from exam_service import read_prompt, gemini_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

@dataclass
class CheatingDetectionResult:
    """Result from the cheating detection analysis."""
    is_cheating: bool
    confidence: str
    summary: str
    indicators_found: list
    recommendation: str
    notes: str


async def detect_cheating(
    audio: bytes,
    video: bytes,
    audio_mime_type: str = "audio/webm",
    video_mime_type: str = "video/webm",
) -> CheatingDetectionResult:
    """
    Analyze audio and video from an oral exam to detect potential cheating.

    Args:
        audio: Audio bytes from the oral exam recording
        video: Video bytes from the oral exam recording
        audio_mime_type: MIME type of the audio file
        video_mime_type: MIME type of the video file

    Returns:
        CheatingDetectionResult with analysis of potential cheating indicators
    """
    logger.info("=" * 60)
    logger.info("[Cheating Detection] Starting analysis...")
    logger.info("=" * 60)

    # Read the cheating detection prompt
    logger.info("[Cheating Detection] Loading prompt...")
    system_prompt = read_prompt("cheating_detection.txt")

    # Create inline data parts for audio and video
    logger.info("[Cheating Detection] Preparing audio data...")
    audio_part = genai.types.Part.from_bytes(
        data=audio,
        mime_type=audio_mime_type,
    )
    logger.info("[Cheating Detection] Preparing video data...")
    video_part = genai.types.Part.from_bytes(
        data=video,
        mime_type=video_mime_type,
    )

    prompt_text = "Please analyze this audio and video recording from an oral exam for any signs of cheating or academic dishonesty. Provide your analysis in the specified JSON format."

    # Call Gemini with both audio and video
    logger.info("[Gemini] Sending audio/video for cheating analysis...")
    response = await asyncio.to_thread(
        gemini_client.models.generate_content,
        model="gemini-3-pro-preview",
        contents=[audio_part, video_part, prompt_text],
        config=genai.types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.5,  # Lower temperature for more consistent analysis
        ),
    )
    logger.info("[Gemini] Cheating analysis response received")

    # Parse the JSON response
    logger.info("[Cheating Detection] Parsing analysis results...")
    response_text = response.text.strip()

    # Extract JSON from the response (handle markdown code blocks if present)
    if "```json" in response_text:
        json_start = response_text.find("```json") + 7
        json_end = response_text.find("```", json_start)
        response_text = response_text[json_start:json_end].strip()
    elif "```" in response_text:
        json_start = response_text.find("```") + 3
        json_end = response_text.find("```", json_start)
        response_text = response_text[json_start:json_end].strip()

    result_data = json.loads(response_text)

    result = CheatingDetectionResult(
        is_cheating=result_data.get("is_cheating", False),
        confidence=result_data.get("confidence", "low"),
        summary=result_data.get("summary", ""),
        indicators_found=result_data.get("indicators_found", []),
        recommendation=result_data.get("recommendation", "clear"),
        notes=result_data.get("notes", ""),
    )

    logger.info("=" * 60)
    cheating_status = "DETECTED" if result.is_cheating else "CLEAR"
    logger.info(f"[Cheating Detection] RESULT: {cheating_status}")
    logger.info(f"   Confidence: {result.confidence}")
    logger.info(f"   Recommendation: {result.recommendation}")
    logger.info("=" * 60)

    return result