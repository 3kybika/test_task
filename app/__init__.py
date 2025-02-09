import os
from dotenv import load_dotenv
from app.core.settings import Settings

# load .env file
load_dotenv(os.environ.get("ENV_FILE"))

settings = Settings()
