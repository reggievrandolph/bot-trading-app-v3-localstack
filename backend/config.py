import os
from dotenv import load_dotenv

load_dotenv()

CS_APP_KEY = os.getenv("CS_APP_KEY")
CS_APP_SECRET = os.getenv("CS_APP_SECRET")
CS_CALLBACK_URL = os.getenv("CS_CALLBACK_URL")
