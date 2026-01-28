from fastapi import APIRouter, UploadFile, File
from services.exam_service import process_exam

router = APIRouter()


@router.post("/analyze")
async def analyze(audio: UploadFile = File(...), video: UploadFile = File(...)) -> int:
    """
    Accepts audio and video files, processes them through AI clients,
    and returns a hardcoded result.
    """
    audio_bytes = await audio.read()
    video_bytes = await video.read()
    
    claude_final_response, gemini_final_response = await process_exam(audio_bytes, video_bytes)
    
    # Currently returns hardcoded 100
    return 100
