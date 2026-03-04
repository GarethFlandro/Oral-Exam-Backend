import io
import json
import os
import uuid
import zipfile

from fastapi import APIRouter, UploadFile, File, Form, Depends, Response, Cookie, HTTPException, status
from fastapi.responses import StreamingResponse
from fastapi.security import APIKeyHeader

from services.anticheat import detect_cheating
from services.exam_service import process_exam
from services.voice_transcripts import generate_speech

router = APIRouter()

STATIC_API_KEY = os.getenv("ORAL_EXAM_API_KEY")
api_key_header = APIKeyHeader(name="API_KEY", auto_error=True)


def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key == STATIC_API_KEY:
        return api_key
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate API key",
    )


@router.post("/analyze-exam", dependencies=[Depends(get_api_key)])
async def analyze_exam(
        audio: UploadFile = File(...),
        class_name: str = Form(...),
) -> dict:
    """
    Accepts audio file, processes them through AI clients,
    and returns the averaged grade from both models.

    Args:
        audio: The audio file from the oral exam (supports .webm, .m4a, .mp4)
        class_name: The name of the class being taught

    Returns:
        JSON response with:
        - success: Boolean indicating if the analysis completed successfully
        - grade: The averaged grade from both models
        - class_name: The class that was evaluated
    """
    audio_bytes = await audio.read()

    # Get the content type from the uploaded file, default to audio/webm
    mime_type = audio.content_type or "audio/webm"

    average_grade, gemini1_grade, claude1_grade, gemini2_grade, claude2_grade = await process_exam(audio_bytes, class_name, mime_type)

    return {
        "grade": average_grade,
        "class_name": class_name,
        "gemini_initial_grade": gemini1_grade,
        "claude_initial_grade": claude1_grade,
        "gemini_review_grade": gemini2_grade,
        "claude_review_grade": claude2_grade,
    }


@router.post("/detect-cheating", dependencies=[Depends(get_api_key)])
async def detect_cheating_endpoint(
        exam_audio: UploadFile = File(...),
        student_video: UploadFile = File(...),
        student_screen: UploadFile = File(...),
) -> dict:
    """
    Analyzes audio and video from an oral exam to detect potential cheating.

    Args:
        exam_audio: The audio file from the oral exam
        student_video: The video of the student during the oral exam
        student_screen: The screen recording of the student's computer during the exam

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
    exam_audio_bytes = await exam_audio.read()
    student_video_bytes = await student_video.read()
    student_screen_bytes = await student_screen.read()

    # Get MIME types from uploaded files
    exam_audio_mime_type = exam_audio.content_type or "audio/webm"
    student_video_mime_type = student_video.content_type or "video/webm"
    student_screen_mime_type = student_screen.content_type or "video/webm"

    result = await detect_cheating(
        exam_audio=exam_audio_bytes,
        student_video=student_video_bytes,
        student_screen=student_screen_bytes,
        exam_audio_mime_type=exam_audio_mime_type,
        student_video_mime_type=student_video_mime_type,
        student_screen_mime_type=student_screen_mime_type,
    )

    return {
        "is_cheating": result.is_cheating,
        "confidence": result.confidence,
        "summary": result.summary,
        "indicators_found": result.indicators_found,
        "recommendation": result.recommendation,
        "notes": result.notes,
    }


@router.post("/generate-speech", dependencies=[Depends(get_api_key)])
async def generate_speech_endpoint(
        questions: str = Form(...),
) -> StreamingResponse:
    """
    Generate speech audio files from a list of question strings.

    Args:
        questions: A JSON string in format:
            {
                "items": [
                    "What is the capital of France?",
                    "Explain the theory of relativity.",
                    ...
                ]
            }

    Returns:
        A ZIP file containing MP3 audio files for each question.
        Each audio file is named question_0.mp3, question_1.mp3, etc.
    """
    # Parse the JSON string to get the items array
    questions_data = json.loads(questions)
    question_list = questions_data["items"]

    # Create an in-memory ZIP file
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for index, question_text in enumerate(question_list):
            # Generate audio for each question using ElevenLabs
            audio_bytes = generate_speech(question_text)

            # Add the audio file to the ZIP archive
            filename = f"question_{index}.mp3"
            zip_file.writestr(filename, audio_bytes)

    # Seek to the beginning of the buffer for reading
    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=questions_audio.zip"}
    )


# List of active users (in-memory, we don't really care if everyone is logged out when the server restarts)
logged_in_users = {}


@router.post("/login", dependencies=[Depends(get_api_key)])
def login(response: Response, email: str):
    # Generate a random session ID
    session_id = str(uuid.uuid4())

    # Add to your list
    logged_in_users[session_id] = email

    # Give the session ID to the user as a cookie
    response.set_cookie(key="session_token", value=session_id)
    return {"message": f"Successfully logged in as {email}"}


@router.post("/logout", dependencies=[Depends(get_api_key)])
def logout(response: Response, session_token: str = Cookie(None)):
    # Remove from list
    if session_token in logged_in_users:
        del logged_in_users[session_token]

    # Tell the browser to delete the cookie
    response.delete_cookie("session_token")
    return {"message": "Logged out"}