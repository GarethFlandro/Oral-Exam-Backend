import asyncio
import logging
from pathlib import Path

import anthropic
import google.genai as genai

from config.api_keys import CLAUDE_API_KEY, GEMINI_API_KEY
from services.transcription import transcribe_audio_with_gemini

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# Path to prompts directory
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

# Initialize client
gemini_client = genai.Client(api_key=GEMINI_API_KEY)
claude_client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)


def read_prompt(filename: str) -> str:
    """Read a prompt file from the prompts directory."""
    prompt_path = PROMPTS_DIR / filename
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(filename: str, content: str):
    """Write content to a file in the prompts directory."""
    file_path = Path(__file__).parent.parent / "responses" / filename
    with open(file_path, "r+", encoding="utf-8") as f:
        f.write(content)


async def call_gemini(
    audio: bytes,
    system_prompt: str,
    mime_type: str = "audio/webm",
    temperature: float = 1.0,
) -> str:
    """
    Call Gemini API with audio content.

    Args:
        audio: Audio bytes to analyze
        system_prompt: System instruction for the model
        mime_type: MIME type of the audio file
        temperature: Sampling temperature (higher = more creative)
    """
    # Create inline data part for audio
    audio_part = genai.types.Part.from_bytes(
        data=audio,
        mime_type=mime_type,
    )

    prompt_text = "Please analyze this audio recording from an oral exam."

    # Run sync Gemini call in thread pool to maintain async compatibility
    logger.info("gemini 1 has commenced")
    response = await asyncio.to_thread(
        gemini_client.models.generate_content,
        model="gemini-3-flash-preview",
        contents=[audio_part, prompt_text],
        config=genai.types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=temperature,
        ),
    )

    logger.info(f"gemini 1 has ceased")
    write_file("gemini1.txt", response.text)
    return response.text


async def call_gemini_with_peer_response(
    audio: bytes,
    peer_response: str,
    peer_prompt: str,
    mime_type: str = "audio/webm",
    temperature: float = 1.0
) -> str:
    """
    Call Gemini API to review and respond to the peer model's response.

    Args:
        audio: Audio bytes from the original recording
        peer_response: The other model's analysis
        peer_prompt: System instruction for the review
        mime_type: MIME type of the audio file
        temperature: Sampling temperature (higher = more creative)
    """
    logger.info("gemini 2 has commenced")

    # Create inline data part for audio
    audio_part = genai.types.Part.from_bytes(
        data=audio,
        mime_type=mime_type,
    )

    prompt = f"Here is the other AI's analysis of the oral exam:\n\n{peer_response}\n\nPlease provide your final assessment considering this input and the audio recording."

    # Run sync Gemini call in thread pool to maintain async compatibility
    response = await asyncio.to_thread(
        gemini_client.models.generate_content,
        model="gemini-3-flash-preview",
        contents=[audio_part, prompt],
        config=genai.types.GenerateContentConfig(
            system_instruction=peer_prompt,
            temperature=temperature,
        ),
    )

    logger.info(f"gemini 2 has ceased")
    write_file("gemini2.txt", response.text)
    return response.text


async def call_claude(
    transcript: str,
    system_prompt: str,
) -> str:
    """
    Call Claude API with transcribed audio content.

    Args:
        transcript: Transcribed text from the audio recording
        system_prompt: System instruction for the model
    """
    prompt_text = f"Please analyze this transcript from an oral exam recording:\n\n{transcript}"

    # Run Claude call in thread pool to maintain async compatibility
    logger.info("claude 1 has commenced")
    response = await asyncio.to_thread(
        claude_client.messages.create,
        model="claude-sonnet-4-5",
        max_tokens=8192,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": prompt_text,
            }
        ],
    )

    logger.info(f"claude 1 has ceased")
    write_file("claude1.txt", response.content[0].text)
    return response.content[0].text


async def call_claude_with_peer_response(
    transcript: str,
    peer_response: str,
    peer_prompt: str
) -> str:
    """
    Call Claude API to review and respond to the peer model's response.

    Args:
        transcript: Transcribed text from the audio recording
        peer_response: The other model's analysis
        peer_prompt: System instruction for the review
    """
    logger.info("claude 2 has commenced")
    prompt = f"Here is the transcript from the oral exam:\n\n{transcript}\n\nHere is the other AI's analysis of the oral exam:\n\n{peer_response}\n\nPlease provide your final assessment considering both the transcript and this input."

    # Run Claude call in thread pool to maintain async compatibility
    response = await asyncio.to_thread(
        claude_client.messages.create,
        model="claude-sonnet-4-5",
        max_tokens=8192,
        system=peer_prompt,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    logger.info(f"claude 2 has ceased")
    write_file("claude2.txt", response.content[0].text)
    return response.content[0].text


async def process_exam(
    audio: bytes, class_name: str, mime_type: str = "audio/webm"
) -> int:
    """
    Process the exam audio through Gemini and Claude for diverse evaluation.

    Args:
        audio: The audio bytes from the oral exam recording
        class_name: The name of the class being taught
        mime_type: The MIME type of the audio file

    Steps:
    1. Read prompts from files
    2. Send audio to Gemini and Claude for diverse model evaluation
    3. Exchange responses for peer review
    4. Extract grades from both final responses and average them
    """

    # Step 1: Read prompts and transcribe audio
    first_stage_prompt = read_prompt("first_stage.txt")
    first_stage_prompt = first_stage_prompt.replace("{class_name}", class_name)
    second_stage_prompt = read_prompt("second_stage.txt")
    second_stage_prompt = second_stage_prompt.replace("{class_name}", class_name)

    # Transcribe audio once for Claude to use
    logger.info("transcription has commenced")
    transcript = await transcribe_audio_with_gemini(
        audio=audio,
        mime_type=mime_type,
    )
    logger.info(f"transcription has ceased")

    # Step 2: Send audio to Gemini and transcript to Claude for diverse model evaluation
    gemini_response = await call_gemini(
        audio, first_stage_prompt, mime_type
    )
    claude_response = await call_claude(
        transcript, first_stage_prompt
    )

    # Step 3: Exchange responses - each instance reviews the other's analysis
    gemini_final = await call_gemini_with_peer_response(
        audio, claude_response, second_stage_prompt, mime_type
    )
    claude_final = await call_claude_with_peer_response(
        transcript, gemini_response, second_stage_prompt
    )

    # Step 4: Extract grades and compute average
    grade_1 = await convert_report_to_int(gemini_final)
    logger.info(f"gemini grade obtained: {grade_1}")
    grade_2 = await convert_report_to_int(claude_final)
    logger.info(f"claude grade obtained: {grade_2}")

    average_grade = round((grade_1 + grade_2) / 2)

    logger.info(f"average grade is: {average_grade}")
    return average_grade


async def convert_report_to_int(report: str) -> int:
    """
    Extract the integer grade from a full review report using Gemini Flash 2.0.

    Args:
        report: A full review text that contains a final score somewhere in it.

    Returns:
        The single integer grade found in the report.
    """
    prompt = f"Extract the final grade/score from this review and return only the integer:\n\n{report}"

    # Run sync Gemini call in thread pool to maintain async compatibility (puts it in another thread so the main program can continue in the current one)
    response = await asyncio.to_thread(
        gemini_client.models.generate_content,
        model="gemini-2.5-flash",
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            system_instruction=read_prompt("find_final_score.txt"),
        ),
    )

    # Parse the response to get the integer
    grade_text = response.text.strip()
    return int(grade_text)