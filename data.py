from dotenv import load_dotenv
import os

load_dotenv()

Token = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

