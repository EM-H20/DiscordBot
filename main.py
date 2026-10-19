#====================================메인 진입점======================================
# 로스트아크 디스코드 봇의 메인 진입점입니다.
# 리팩토링 버전 - 모듈화된 구조
#
# 구조:
# ├── main.py          <- 진입점 (현재 파일)
# ├── data.py          <- 환경변수 로드
# ├── config.py        <- 상수 설정
# ├── bot/
# │   └── bot.py       <- 봇 클래스 및 초기화
# ├── cogs/
# │   ├── admin.py     <- 관리 명령어
# │   ├── help.py      <- 도움말 명령어
# │   ├── notice.py    <- 공지사항 명령어
# │   ├── chatbot.py   <- Gemini AI 챗봇
# │   ├── policy.py    <- 정책사항 명령어
# │   ├── schedule.py  <- 투표 명령어
# │   └── boss_strategy.py <- 보스 공략 명령어
# ├── ui/
# │   └── poll_views.py <- 투표 UI 컴포넌트
# └── utils/
#     └── date_utils.py <- 날짜 유틸리티 함수

from data import Token
from bot.bot import create_bot


def main():
    """봇을 실행합니다."""
    bot = create_bot()
    bot.run(Token)


if __name__ == '__main__':
    main()
