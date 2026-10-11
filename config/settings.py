# config/settings.py
import os
from dotenv import load_dotenv
from pathlib import Path

# Naloži .env
load_dotenv()

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

# Ustvari static folder
STATIC_DIR.mkdir(exist_ok=True)

# Microsoft 365
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:8501")
AUTHORITY = "https://login.microsoftonline.com/common"
AUTH_URL = f"{AUTHORITY}/oauth2/v2.0/authorize"
TOKEN_URL = f"{AUTHORITY}/oauth2/v2.0/token"

# Microsoft Graph API scopes
SCOPES = [
    "Calendars.Read",
    "Calendars.ReadWrite",
    "User.Read",
    "offline_access",
    "Tasks.ReadWrite",
    "OnlineMeetings.Read",
    "Notes.ReadWrite",        
    "Notes.ReadWrite.All",
    "Files.ReadWrite",         
    "Mail.Read",           
    "Mail.ReadWrite",
]

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# App settings
APP_NAME = os.getenv("APP_NAME", "Meeting Assistant")
APP_VERSION = "2.0.0"
DEBUG = os.getenv("DEBUG", "False").lower() == "true"