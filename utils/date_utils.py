#====================================날짜 유틸리티======================================
# 날짜 관련 공통 함수들을 관리합니다.

from datetime import datetime
from config import KOREAN_WEEKDAYS


def get_korean_weekday(date_obj: datetime) -> str:
    """
    날짜 객체에서 한국어 요일 반환
    :param date_obj: datetime 객체
    :return: 한국어 요일 (월, 화, 수, 목, 금, 토, 일)
    """
    return KOREAN_WEEKDAYS[date_obj.weekday()]


def format_korean_date(date_str: str) -> str:
    """
    날짜 문자열을 한국어 형식으로 변환
    :param date_str: 'YYYY-MM-DD' 형식의 날짜 문자열
    :return: 'M월 D일 (요일)' 형식의 문자열
    """
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    weekday = get_korean_weekday(date_obj)
    return f"{date_obj.month}월 {date_obj.day}일 ({weekday})"


def format_korean_date_full(date_str: str) -> str:
    """
    날짜 문자열을 연도 포함 한국어 형식으로 변환
    :param date_str: 'YYYY-MM-DD' 형식의 날짜 문자열
    :return: 'YYYY년 M월 D일' 형식의 문자열
    """
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    return f"{date_obj.year}년 {date_obj.month}월 {date_obj.day}일"


def create_progress_bar(count: int, max_count: int, total_length: int = 10) -> str:
    """
    투표 진행률 바 생성
    :param count: 현재 투표 수
    :param max_count: 최대 투표 수
    :param total_length: 바의 총 길이 (기본값 10)
    :return: 이모지로 구성된 진행률 바 문자열
    """
    if max_count == 0:
        return "⬜" * total_length
    filled = round(count / max_count * total_length)
    return "🟦" * filled + "⬜" * (total_length - filled)


def validate_date_format(date_str: str) -> bool:
    """
    날짜 형식 검증 (YYYY-MM-DD)
    :param date_str: 검증할 날짜 문자열
    :return: 유효하면 True, 아니면 False
    """
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def parse_date(date_str: str) -> datetime:
    """
    날짜 문자열을 datetime 객체로 변환
    :param date_str: 'YYYY-MM-DD' 형식의 날짜 문자열
    :return: datetime 객체
    """
    return datetime.strptime(date_str, '%Y-%m-%d')
