import asyncio
from pathlib import Path

from google import genai

from config.api_keys import GEMINI_API_KEY

# Path to prompts directory
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

# Initialize client
gemini_client = genai.Client(api_key=GEMINI_API_KEY)


def read_prompt(filename: str) -> str:
    """Read a prompt file from the prompts directory."""
    prompt_path = PROMPTS_DIR / filename
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


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
    response = await asyncio.to_thread(
        gemini_client.models.generate_content,
        model="gemini-3-pro-preview",
        contents=[audio_part, prompt_text],
        config=genai.types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=temperature,
        ),
    )

    return response.text


async def call_gemini_with_peer_response(
    peer_response: str, peer_prompt: str, temperature: float = 1.0
) -> str:
    """
    Call Gemini API to review and respond to the peer model's response.

    Args:
        peer_response: The other model's analysis
        peer_prompt: System instruction for the review
        temperature: Sampling temperature (higher = more creative)
    """
    prompt = f"Here is the other AI's analysis of the oral exam:\n\n{peer_response}\n\nPlease provide your final assessment considering this input."

    # Run sync Gemini call in thread pool to maintain async compatibility
    response = await asyncio.to_thread(
        gemini_client.models.generate_content,
        model="gemini-3-pro-preview",
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            system_instruction=peer_prompt,
            temperature=temperature,
        ),
    )

    return response.text


async def process_exam(
    audio: bytes, class_name: str, mime_type: str = "audio/webm"
) -> int:
    """
    Process the exam audio through two Gemini instances with different temperatures.

    Args:
        audio: The audio bytes from the oral exam recording
        class_name: The name of the class being taught
        mime_type: The MIME type of the audio file

    Steps:
    1. Read prompts from files
    2. Send audio to Gemini twice: once with normal temp, once with higher temp
    3. Exchange responses for peer review
    4. Extract grades from both final responses and average them
    """
    # Step 1: Read prompts
    first_stage_prompt = read_prompt("first_stage.txt")
    first_stage_prompt = first_stage_prompt.replace("{class_name}", class_name)
    second_stage_prompt = read_prompt("second_stage.txt")
    second_stage_prompt = second_stage_prompt.replace("{class_name}", class_name)

    # Step 2: Send audio to Gemini with two different temperatures for diversity
    gemini_response_1 = await call_gemini(
        audio, first_stage_prompt, mime_type, temperature=1.0
    )
    gemini_response_2 = await call_gemini(
        audio, first_stage_prompt, mime_type, temperature=1.5
    )

    # Step 3: Exchange responses - each instance reviews the other's analysis
    gemini_final_1 = await call_gemini_with_peer_response(
        gemini_response_2, second_stage_prompt, temperature=1.0
    )
    gemini_final_2 = await call_gemini_with_peer_response(
        gemini_response_1, second_stage_prompt, temperature=1.5
    )

    # Step 4: Extract grades and compute average
    grade_1 = await convert_report_to_int(gemini_final_1)
    grade_2 = await convert_report_to_int(gemini_final_2)

    average_grade = round((grade_1 + grade_2) / 2)

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
        model="gemini-2.0-flash",
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            system_instruction=read_prompt("find_final_score.txt"),
        ),
    )

    # Parse the response to get the integer
    grade_text = response.text.strip()
    return int(grade_text)
