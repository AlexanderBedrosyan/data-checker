# app/config.py
import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    DEBUG = os.getenv('DEBUG', 'False') == 'True'

