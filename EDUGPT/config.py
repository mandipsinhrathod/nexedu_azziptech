import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_key_very_secret_123'
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or ''
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'edugpt_db'
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    GROK_API_KEY = os.environ.get('GROK_API_KEY')
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
