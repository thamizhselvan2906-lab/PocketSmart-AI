import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / ".env")

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "pocketsmart-ai-secret-key-change-in-prod-2026")
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    
    # Database
    DATABASE_PATH = BASE_DIR / "pocketsmart.db"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI", f"sqlite:///{DATABASE_PATH}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Uploads
    UPLOAD_FOLDER = BASE_DIR / "uploads"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
    
    # Static files directory
    FRONTEND_DIR = BASE_DIR / "frontend"

# Ensure directories exist
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
