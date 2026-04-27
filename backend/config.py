import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    ADMIN_TOKEN: str = os.getenv("ADMIN_TOKEN", "dev-token")
    BASE_INCOME: int = 5_000

settings = Settings()
