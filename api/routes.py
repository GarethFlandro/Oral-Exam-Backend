from fastapi import APIRouter, UploadFile, File, Form
from services.exam_service import process_exam

router = APIRouter()


@router.post("/analyze")
async def analyze(
    audio: UploadFile = File(...),
    video: UploadFile = File(...),
    class_name: str = Form(...),
) -> int:
    """
    Accepts audio and video files, processes them through AI clients,
    and returns the averaged grade from both models.

    Args:
        audio: The audio file from the oral exam (supports .webm, .m4a, .mp4)
        video: The video file (stored for potential anticheat analysis)
        class_name: The name of the class being taught
    """
    audio_bytes = await audio.read()
    video_bytes = (
        await video.read()
    )  # Video stored but might be sent eventually to an anticheat model

    # Get the content type from the uploaded file, default to audio/webm
    mime_type = audio.content_type or "audio/webm"

    average_grade = await process_exam(audio_bytes, class_name, mime_type)

    return average_grade
