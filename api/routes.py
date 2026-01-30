from fastapi import APIRouter, UploadFile, File, Form
from services.exam_service import process_exam, detect_cheating

router = APIRouter()


@router.post("/analyze")
async def analyze(
    audio: UploadFile = File(...),
    video: UploadFile = File(...),
    class_name: str = Form(...),
) -> dict:
    """
    Accepts audio and video files, processes them through AI clients,
    and returns the averaged grade from both models.

    Args:
        audio: The audio file from the oral exam (supports .webm, .m4a, .mp4)
        video: The video file (stored for potential anticheat analysis)
        class_name: The name of the class being taught

    Returns:
        JSON response with:
        - success: Boolean indicating if the analysis completed successfully
        - grade: The averaged grade from both models
        - class_name: The class that was evaluated
    """
    audio_bytes = await audio.read()
    video_bytes = (
        await video.read()
    )  # Video stored but might be sent eventually to an anticheat model

    # Get the content type from the uploaded file, default to audio/webm
    mime_type = audio.content_type or "audio/webm"

    average_grade = await process_exam(audio_bytes, class_name, mime_type)

    return {
        "success": True,
        "grade": average_grade,
        "class_name": class_name,
    }


@router.post("/detect-cheating")
async def detect_cheating_endpoint(
    audio: UploadFile = File(...),
    video: UploadFile = File(...),
) -> dict:
    """
    Analyzes audio and video from an oral exam to detect potential cheating.

    Args:
        audio: The audio file from the oral exam (supports .webm, .m4a, .mp4)
        video: The video file from the oral exam (supports .webm, .mp4)

    Returns:
        JSON response with:
        - success: Boolean indicating if the analysis completed successfully
        - is_cheating: Boolean indicating if cheating was detected
        - confidence: Level of confidence (low/medium/high)
        - summary: Brief summary of the analysis
        - indicators_found: List of specific indicators observed
        - recommendation: clear/review/flag
        - notes: Additional context
    """
    audio_bytes = await audio.read()
    video_bytes = await video.read()

    # Get MIME types from uploaded files
    audio_mime_type = audio.content_type or "audio/webm"
    video_mime_type = video.content_type or "video/webm"

    result = await detect_cheating(
        audio=audio_bytes,
        video=video_bytes,
        audio_mime_type=audio_mime_type,
        video_mime_type=video_mime_type,
    )

    return {
        "success": True,
        "is_cheating": result.is_cheating,
        "confidence": result.confidence,
        "summary": result.summary,
        "indicators_found": result.indicators_found,
        "recommendation": result.recommendation,
        "notes": result.notes,
    }

