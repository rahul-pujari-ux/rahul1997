import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.model = os.getenv("MODEL", "global.anthropic.claude-sonnet-4-6")
        self.fastapi_port = int(os.getenv("FASTAPI_PORT", 8000))
        self.streamlit_port = int(os.getenv("STREAMLIT_PORT", 8501))
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./loan_assist.db")

settings = Settings()
