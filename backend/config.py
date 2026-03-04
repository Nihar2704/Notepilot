import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CACHE_DB_PATH = os.getenv("CACHE_DB_PATH", "data/notepilot.db")
MODEL_NAME = "llama-3.1-8b-instant"

if not GROQ_API_KEY:
    print("Warning: GROQ_API_KEY not found in environment variables.")
