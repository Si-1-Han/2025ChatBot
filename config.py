from dotenv import load_dotenv
import os

load_dotenv()

DEBUG = os.getenv("DEBUG", "True") == "True"
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 5000))

DB_PATH = os.getenv("DB_PATH", "chatbot.db")
