from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from services.exam_service import process_exam
from services.anticheat import detect_cheating
from services.voice_transcripts import generate_speech
import json
import zipfile
import io

router = APIRouter()


@router.post("/analyze-exam")
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

    average_grade = await process_exam(audio_bytes, class_name, mime_type)

    return {
        "grade": average_grade,
        "class_name": class_name,
    }


@router.post("/detect-cheating")
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
        "success": True,
        "is_cheating": result.is_cheating,
        "confidence": result.confidence,
        "summary": result.summary,
        "indicators_found": result.indicators_found,
        "recommendation": result.recommendation,
        "notes": result.notes,
    }


@router.post("/generate-speech")
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