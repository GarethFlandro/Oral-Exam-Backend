# API Keys for AI clients
import os


CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", default=None)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", default=None)
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", default=None)
ORAL_EXAM_API_KEY = os.getenv("ORAL_EXAM_API_KEY", default=None)
OAUTH_CLIENT_ID = os.getenv("OAUTH_CLIENT_ID", default=None)