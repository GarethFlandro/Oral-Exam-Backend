from fastapi import APIRouter, UploadFile, File
from services.exam_service import process_exam

router = APIRouter()


@router.post("/analyze")
async def analyze(audio: UploadFile = File(...), video: UploadFile = File(...)) -> int:
    """
    Accepts audio and video files, processes them through AI clients,
    and returns the averaged grade from both models.
    """
    audio_bytes = await audio.read()
    video_bytes = await video.read()
    
    average_grade = await process_exam(audio_bytes, video_bytes)
    
    return average_grade
