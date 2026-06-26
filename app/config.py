from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    APP_NAME: str = "Chef Rolex API"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    @property
    def GROQ_API_KEY(self) -> str:
        key = os.getenv("GROQ_API_KEY", "")
        if not key:
            key = os.getenv("GROQ_API_URL", "") # Fallback just in case!
        return key.strip()
        
    @property
    def DATABASE_URL(self) -> str:
        return os.getenv("DATABASE_URL", "").strip()

    MODEL_NAME: str = "llama-3.3-70b-versatile"
    TEMPERATURE: float = 0.7
    MAX_HISTORY: int = 50

settings = Settings()