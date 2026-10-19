from dotenv import load_dotenv
import os

load_dotenv()

Token = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# 개발모드 여부 확인 (DEV_MODE가 'true'면 개발모드)
DEV_MODE = os.getenv('DEV_MODE', 'false').lower() == 'true'

# 개발모드면 TEST_CHANNEL_ID, 운영모드면 CHANNEL_ID 사용
CHANNEL_ID = os.getenv('TEST_CHANNEL_ID') if DEV_MODE else os.getenv('CHANNEL_ID')
