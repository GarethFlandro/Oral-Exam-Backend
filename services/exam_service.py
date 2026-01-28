import base64
import asyncio
from pathlib import Path

import anthropic
import google.generativeai as genai

from config.api_keys import CLAUDE_API_KEY, GEMINI_API_KEY

# Path to prompts directory
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

# Initialize clients
claude_client = anthropic.AsyncAnthropic(api_key=CLAUDE_API_KEY)
genai.configure(api_key=GEMINI_API_KEY)


def read_prompt(filename: str) -> str:
    """Read a prompt file from the prompts directory."""
    prompt_path = PROMPTS_DIR / filename
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def encode_to_base64(data: bytes) -> str:
    """Encode bytes to base64 string."""
    return base64.standard_b64encode(data).decode("utf-8")


async def call_claude(audio: bytes, video: bytes, system_prompt: str) -> str:
    """
    Call Claude API with audio and video content.
    Claude supports audio natively; video is sent as a note since Claude doesn't support video directly.
    """
    audio_b64 = encode_to_base64(audio)
    
    message = await claude_client.messages.create(
        model="claude-opus-4-5-20251101",
        max_tokens=4096,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "audio/webm",
                            "data": audio_b64,
                        },
                    },
                    {
                        "type": "text",
                        "text": "Please analyze this audio recording from an oral exam. Note: A video file was also provided but cannot be processed directly.",
                    },
                ],
            }
        ],
    )
    
    return message.content[0].text


async def call_gemini(audio: bytes, video: bytes, system_prompt: str) -> str:
    """
    Call Gemini API with audio and video content.
    Gemini supports multimodal input including audio and video.
    """
    model = genai.GenerativeModel(
        model_name="gemini-3-pro-preview",
        system_instruction=system_prompt,
    )
    
    # Create inline data parts for audio and video
    audio_part = {
        "inline_data": {
            "mime_type": "audio/webm",
            "data": encode_to_base64(audio),
        }
    }
    
    video_part = {
        "inline_data": {
            "mime_type": "video/mp4",
            "data": encode_to_base64(video),
        }
    }
    
    prompt_text = "Please analyze this audio and video recording from an oral exam."
    
    # Run sync Gemini call in thread pool to maintain async compatibility
    response = await asyncio.to_thread(
        model.generate_content,
        [audio_part, video_part, prompt_text],
    )
    
    return response.text


async def call_claude_with_peer_response(peer_response: str, peer_prompt: str) -> str:
    """
    Call Claude API to review and respond to the peer model's (Gemini's) response.
    """
    message = await claude_client.messages.create(
        model="claude-opus-4-5-20251101",
        max_tokens=4096,
        system=peer_prompt,
        messages=[
            {
                "role": "user",
                "content": f"Here is the other AI's analysis of the oral exam:\n\n{peer_response}\n\nPlease provide your final assessment considering this input.",
            }
        ],
    )
    
    return message.content[0].text


async def call_gemini_with_peer_response(peer_response: str, peer_prompt: str) -> str:
    """
    Call Gemini API to review and respond to the peer model's (Claude's) response.
    """
    model = genai.GenerativeModel(
        model_name="gemini-3-pro-preview",
        system_instruction=peer_prompt,
    )
    
    prompt = f"Here is the other AI's analysis of the oral exam:\n\n{peer_response}\n\nPlease provide your final assessment considering this input."
    
    # Run sync Gemini call in thread pool to maintain async compatibility
    response = await asyncio.to_thread(
        model.generate_content,
        prompt,
    )
    
    return response.text


async def process_exam(audio: bytes, video: bytes) -> int:
    """
    Process the exam audio and video through Claude and Gemini.
    
    Steps:
    1. Read prompts from files
    2. Send files + system prompt to Claude and Gemini
    3. Exchange responses using peer_response_prompt
    4. Extract grades from both final responses and average them
    """
    # Step 1: Read prompts
    system_prompt = read_prompt("system_prompt.txt")
    peer_response_prompt = read_prompt("peer_response_prompt.txt")
    
    # Step 2: Send files + system prompt to both AI clients
    claude_initial_response = await call_claude(audio, video, system_prompt)
    gemini_initial_response = await call_gemini(audio, video, system_prompt)
    
    # Step 3: Exchange responses - send each model's response to the other
    # Send Claude's response to Gemini with peer_response_prompt
    gemini_final_response = await call_gemini_with_peer_response(
        claude_initial_response, peer_response_prompt
    )
    
    # Send Gemini's response to Claude with peer_response_prompt
    claude_final_response = await call_claude_with_peer_response(
        gemini_initial_response, peer_response_prompt
    )
    
    # Step 4: Extract grades and compute average
    claude_grade = await convert_report_to_int(claude_final_response)
    gemini_grade = await convert_report_to_int(gemini_final_response)
    
    average_grade = round((claude_grade + gemini_grade) / 2)
    
    return average_grade


async def convert_report_to_int(report: str) -> int:
    """
    Extract the integer grade from a full review report using Gemini Flash 2.0.
    
    Args:
        report: A full review text that contains a final score somewhere in it.
        
    Returns:
        The single integer grade found in the report.
    """
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        system_instruction=read_prompt("report_to_int_prompt.txt"),
    )
    
    prompt = f"Extract the final grade/score from this review and return only the integer:\n\n{report}"
    
    # Run sync Gemini call in thread pool to maintain async compatibility
    response = await asyncio.to_thread(
        model.generate_content,
        prompt,
    )
    
    # Parse the response to get the integer
    grade_text = response.text.strip()
    return int(grade_text)
