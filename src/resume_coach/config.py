import os 
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# MODEL = "llama-3.1-8b-instant"

MODEL = "llama-3.3-70b-versatile"
TEMPERATURE = 0.3

MAX_MESSAGES_BEFORE_SUMMARY = 4
MAX_SEARCH_RESULTS = 1

if not GROQ_API_KEY:
    raise EnvironmentError("GROQ_API_KEY is missing. Add it to your .env file.")

if not TAVILY_API_KEY:
    raise EnvironmentError("TAVILY_API_KEY is missing. Add it to your .env file.")
