import os
from dotenv import load_dotenv


load_dotenv()


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

FREE_DAILY_ANALYSES = 5

EXTRA_ANALYSIS_STARS = 20
FULL_ANALYSIS_STARS = 100

SERVER_HOST = os.getenv(
    "SERVER_HOST",
    "0.0.0.0"
)

SERVER_PORT = int(
    os.getenv(
        "SERVER_PORT",
        "8000"
    )
)

PHOTO_DIR = "data/photos"