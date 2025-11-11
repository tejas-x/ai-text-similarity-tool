import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB = os.getenv("MONGO_DB", "ai_assignment_platform")
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
    REPORT_FOLDER = os.path.join(os.path.dirname(__file__), "reports", "generated_reports")
    ALLOWED_EXTENSIONS = {"pdf", "docx"}
    USE_EMBEDDINGS = os.getenv("USE_EMBEDDINGS", "false").lower() == "true"