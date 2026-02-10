import json
from dataclasses import dataclass
import google.genai as genai
import logging
import asyncio

from services.exam_service import read_prompt, gemini_client

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
    exam_audio: bytes,
    student_video: bytes,
    student_screen: bytes,
    exam_audio_mime_type: str = "audio/webm",
    student_video_mime_type: str = "video/webm",
    student_screen_mime_type: str = "video/webm",
) -> CheatingDetectionResult:
    """
    Analyze audio and video from an oral exam to detect potential cheating.

    Args:
        exam_audio: Audio bytes from the oral exam recording
        student_video: Video bytes of the student during the exam
        student_screen: Video bytes of the student's screen recording during the exam
        exam_audio_mime_type: MIME type of the audio file
        student_video_mime_type: MIME type of the student video file
        student_screen_mime_type: MIME type of the screen recording file

    Returns:
        CheatingDetectionResult with analysis of potential cheating indicators
    """

    # Read the cheating detection prompt
    system_prompt = read_prompt("cheating_detection.txt")

    # Create inline data parts for audio, video, and screen recording
    logger.info("got audio data")
    audio_part = genai.types.Part.from_bytes(
        data=exam_audio,
        mime_type=exam_audio_mime_type,
    )
    logger.info("got video data")
    video_part = genai.types.Part.from_bytes(
        data=student_video,
        mime_type=student_video_mime_type,
    )
    logger.info("got screen recording data")
    screen_part = genai.types.Part.from_bytes(
        data=student_screen,
        mime_type=student_screen_mime_type,
    )

    prompt_text = "Please analyze this audio, video recording, and screen recording from an oral exam for any signs of cheating or academic dishonesty. Provide your analysis in the specified JSON format."

    # Call Gemini with audio, video, and screen recording
    logger.info("sending data to gemini")
    response = await asyncio.to_thread(
        gemini_client.models.generate_content,
        model="gemini-3-pro-preview",
        contents=[audio_part, video_part, screen_part, prompt_text],
        config=genai.types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.5,  # lower temperature for more consistent analysis
        ),
    )

    # Parse the JSON response
    logger.info("parsing json")
    response_text = response.text.strip()

    # Extract JSON from the response (handle markdown code blocks if present because ai)
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

    cheating_status = "yes" if result.is_cheating else "no"
    logger.info(f"Was cheating: {cheating_status}")
    logger.info(f"Confidence: {result.confidence}")
    logger.info(f"Recommendation: {result.recommendation}")

    return result