from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    APP_NAME: str = "Chef Rolex API"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    MODEL_NAME: str = "llama-3.3-70b-versatile"
    TEMPERATURE: float = 0.7
    MAX_HISTORY: int = 50

settings = Settings()