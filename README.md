봇을 구동하기 위해서는 
1. 클라우드 서버의 ssh-key 파일, 
2. .env(DISCORD_TOKEN, OPENAI_API_KEY or GEMINI_API_KEY, CHANNEL_ID 에 대한 정보 ex) GEMINI_API_KEY=information)을 따로 만들어서 넣어야합니다.

 pip install -r requirements.txt 명령어를 실행하면 필요 pip 설치가 완료됩니다.

모든 라이브러리의 최신버전을 설치하시려면 pip install -U -r requirements.txt 명령어 실행

기능

1. 초기 코드 최적화
2. 재부팅
3. 상태
4. 챗봇
5. phelp 명령어
    5.1 error 추가
    5.2 Gemini 모델 추가
    5.3 vote 명령어 추가
    5.4 Boss 명령어 추가 
6. 단일투표
7. 중복투표
8. 투표현황
9. 일정표시
10. 투표종료
11. 투표목록
12. 보스공략
13. setup 명령어
