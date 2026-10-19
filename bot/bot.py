#====================================봇 클래스======================================
# Discord 봇의 핵심 클래스를 정의합니다.

import discord
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config import BOT_PREFIX, BOT_ACTIVITY, NOTICE_DAY_OF_WEEK, NOTICE_HOUR, NOTICE_MINUTE


class LostArkBot(commands.Bot):
    """로스트아크 디스코드 봇 클래스"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(command_prefix=BOT_PREFIX, intents=intents)

        # 스케줄러 초기화
        self.scheduler = AsyncIOScheduler()

    async def setup_hook(self):
        """봇 시작 시 Cog 로드 및 스케줄러 설정"""
        # Cog 로드
        cogs = [
            'cogs.admin',
            'cogs.help',
            'cogs.notice',
            'cogs.chatbot',
            'cogs.policy',
            'cogs.schedule',
            'cogs.boss_strategy',
        ]

        for cog in cogs:
            try:
                await self.load_extension(cog)
                print(f"✅ {cog} 로드 완료")
            except Exception as e:
                print(f"❌ {cog} 로드 실패: {e}")

        # 스케줄러 작업 등록 (매주 수요일 10시 05분)
        self._setup_scheduled_tasks()

    def _setup_scheduled_tasks(self):
        """예약된 작업을 설정합니다."""
        from cogs.notice import NoticeCog

        async def send_scheduled_notice():
            """예약된 공지사항 전송"""
            notice_cog = self.get_cog('NoticeCog')
            if notice_cog:
                await notice_cog.send_notice()

        self.scheduler.add_job(
            send_scheduled_notice,
            CronTrigger(
                day_of_week=NOTICE_DAY_OF_WEEK,
                hour=NOTICE_HOUR,
                minute=NOTICE_MINUTE
            )
        )

    async def on_ready(self):
        """봇이 준비되었을 때 호출됩니다."""
        print(f'🤖 {self.user.name}이(가) 연결되었습니다!')
        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Game(BOT_ACTIVITY)
        )

        # 스케줄러 시작
        if not self.scheduler.running:
            self.scheduler.start()
            print("📅 스케줄러가 시작되었습니다.")

    async def on_command_error(self, ctx, error):
        """일반 명령어 오류 처리"""
        if isinstance(error, commands.CommandNotFound):
            # help 명령어가 아닌 경우에만 처리
            if not ctx.message.content.startswith(('/phelp', '/p도움말')):
                await ctx.send("존재하지 않는 명령어입니다. 도움말을 보려면 `/phelp`를 입력하세요.")


def create_bot() -> LostArkBot:
    """봇 인스턴스를 생성하여 반환합니다."""
    return LostArkBot()
