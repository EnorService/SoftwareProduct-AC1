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

