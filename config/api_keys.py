# API Keys for AI clients
import os


CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", default=None)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", default=None)