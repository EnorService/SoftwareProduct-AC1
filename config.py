import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
EXCEL_FILE = DATA_DIR / "lanchonete.xlsx"

load_dotenv(BASE_DIR / ".env")

SECRET_KEY = "chave-local-lanchonete-agil"
HOST = "127.0.0.1"
PORT = 5000

GITHUB_API_URL = "https://api.github.com/graphql"
GITHUB_TOKEN = os.getenv("LANCHONETE_GITHUB_TOKEN", "")
GITHUB_PROJECT_OWNER = os.getenv("LANCHONETE_GITHUB_OWNER", "")
GITHUB_PROJECT_OWNER_TYPE = os.getenv("LANCHONETE_GITHUB_OWNER_TYPE", "user")
GITHUB_PROJECT_NUMBER = os.getenv("LANCHONETE_GITHUB_PROJECT_NUMBER", "")
