import os
from dotenv import load_dotenv

# Sucht automatisch nach der .env Datei im Projekt und lädt sie
load_dotenv()

# Hier weisen wir die geheimen Werte normalen Python-Variablen zu
DROPBOX_TOKEN = os.getenv("DROPBOX_TOKEN")
LLM_API_KEY = os.getenv("MINIMAX2.7") # oder GEMINI_API_KEY
#DB_PATH = os.getenv("DB_PATH", "data/purchases.db") # Mit Standardwert als Fallback

# Optional: Kurzer Check, ob die wichtigsten Keys wirklich da sind
if not DROPBOX_TOKEN:
    raise ValueError("ACHTUNG: DROPBOX_TOKEN fehlt in der .env Datei!")
if not LLM_API_KEY:
    raise ValueError("ACHTUNG: API Key für das LLM fehlt!")