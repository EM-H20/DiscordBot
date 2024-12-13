from dotenv import load_dotenv
import os

load_dotenv()

Token = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
LostArk_API_KEY = os.getenv('LostArk_API_KEY')
CHANNEL_ID = os.getenv('CHANNEL_ID')
