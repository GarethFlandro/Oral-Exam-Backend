import os
from pathlib import Path
from config.api_keys import CLAUDE_API_KEY, GEMINI_API_KEY

# Path to prompts directory
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def read_prompt(filename: str) -> str:
    """Read a prompt file from the prompts directory."""
    prompt_path = PROMPTS_DIR / filename
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


# Mock AI client functions (replace with real SDK calls later)
async def call_claude(audio: bytes, video: bytes, system_prompt: str) -> str:
    """
    Mock Claude API call.
    Replace with actual Anthropic SDK integration.
    """
    # TODO: Implement real Claude API call
    return "Mock Claude initial response"


async def call_gemini(audio: bytes, video: bytes, system_prompt: str) -> str:
    """
    Mock Gemini API call.
    Replace with actual Google Generative AI SDK integration.
    """
    # TODO: Implement real Gemini API call
    return "Mock Gemini initial response"


async def call_claude_with_peer_response(peer_response: str, peer_prompt: str) -> str:
    """
    Mock Claude API call with peer response.
    Replace with actual Anthropic SDK integration.
    """
    # TODO: Implement real Claude API call with peer response
    return "Mock Claude final response after reviewing Gemini's input"


async def call_gemini_with_peer_response(peer_response: str, peer_prompt: str) -> str:
    """
    Mock Gemini API call with peer response.
    Replace with actual Google Generative AI SDK integration.
    """
    # TODO: Implement real Gemini API call with peer response
    return "Mock Gemini final response after reviewing Claude's input"


async def process_exam(audio: bytes, video: bytes) -> tuple[str, str]:
    """
    Process the exam audio and video through Claude and Gemini.
    
    Steps:
    1. Read prompts from files
    2. Send files + system prompt to Claude and Gemini
    3. Exchange responses using peer_response_prompt
    4. Return final responses from both models
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
    
    # Step 4: Return final responses
    return claude_final_response, gemini_final_response
