#====================================도움말 Cog======================================
# 도움말 관련 명령어들을 관리합니다.

import discord
from discord.ext import commands
from config import RAID_CATEGORIES


class HelpCog(commands.Cog):
    """도움말 명령어 Cog"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='phelp', aliases=['p도움말'])
    async def help_command(self, ctx):
        """도움말 명령어"""
        if ctx.invoked_subcommand is None:
            if len(ctx.message.content.split()) > 1:
                # 잘못된 카테고리가 입력된 경우
                embed = self._create_error_embed()
                await ctx.send(embed=embed)
                return

            # 기본 도움말 표시
            embed = self._create_main_help_embed()
            await ctx.send(embed=embed)

    def _create_error_embed(self) -> discord.Embed:
        """오류 임베드 생성"""
        embed = discord.Embed(
            title="❌ 오류",
            description="존재하지 않는 도움말 카테고리입니다.",
            color=discord.Color.red()
        )

        embed.add_field(
            name="사용 가능한 카테고리",
            value=(
                "• `/정책사항` - 정책사이트 링크에 접속\n"
                "• `/공지사항` - 로스트아크 공지사항 홈페이지에 접속\n"
                "• `/phelp 투표` - 투표 관련 명령어\n"
                "• `/phelp 챗봇` - Gemini AI 관련 명령어\n"
                "• `/phelp 보스` - 보스 공략 명령어"
            ),
            inline=False
        )

        embed.set_footer(text="💡 전체 도움말을 보려면 /phelp를 입력하세요.")
        return embed

    def _create_main_help_embed(self) -> discord.Embed:
        """메인 도움말 임베드 생성"""
        embed = discord.Embed(
            title="📋 도움말 카테고리",
            description="원하는 카테고리의 도움말을 보려면 `/phelp [카테고리]`를 입력하세요.",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="📜 정책사항",
            value="정책사항을 보고 싶다면 `/정책사항 or /policy`를 입력하세요.",
            inline=False
        )

        embed.add_field(
            name="🔔 공지사항",
            value="로스트아크 공지사항을 보고 싶다면 `/공지사항 or /notice`를 입력하세요.",
            inline=False
        )

        embed.add_field(
            name="📊 투표",
            value="투표 관련 명령어를 확인하려면 `/phelp 투표`를 입력하세요.",
            inline=False
        )

        embed.add_field(
            name="🤖 챗봇",
            value="Gemini AI 관련 명령어를 확인하려면 `/phelp 챗봇`를 입력하세요.",
            inline=False
        )

        embed.add_field(
            name="🏰 보스",
            value="보스 공략 명령어를 확인하려면 `/phelp 보스`를 입력하세요.",
            inline=False
        )

        embed.set_footer(text="💡 자세한 내용은 개발자에게 문의해주세요!")
        return embed

    @help_command.error
    async def help_error(self, ctx, error):
        """도움말 명령어 오류 처리"""
        if isinstance(error, commands.CommandNotFound):
            embed = self._create_error_embed()
            await ctx.send(embed=embed)

    @help_command.command(name='챗봇')
    async def help_gemini(self, ctx):
        """챗봇 도움말"""
        embed = discord.Embed(
            title="🤖 Gemini AI 명령어 도움말",
            description="Gemini AI 관련 명령어 목록입니다.",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="/질문 [질문내용], /ask [질문내용], /gemini [질문내용], /g [질문내용]",
            value=(
                "Gemini AI에게 질문하기\n"
                "예시) `/질문 파이썬이란 무엇인가요?`"
            ),
            inline=False
        )

        embed.set_footer(text="💡 자세한 내용은 개발자에게 문의해주세요!")
        await ctx.send(embed=embed)

    @help_command.command(name='투표')
    async def help_vote(self, ctx):
        """투표 도움말"""
        embed = discord.Embed(
            title="📊 투표 명령어 도움말",
            description="투표 관련 명령어 목록입니다.",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="📊 투표 종류",
            value=(
                "• 단일투표: 하나의 날짜만 선택 가능 (투표 변경 가능)\n"
                "• 중복투표: 여러 날짜 동시 선택 가능 (매번 새로 선택)"
            ),
            inline=False
        )

        embed.add_field(
            name="📊 /단일투표 [제목] [날짜]",
            value=(
                "단일 투표를 생성합니다.\n"
                "• 제목은 큰따옴표(\")로 감싸주세요!\n"
                "• 날짜는 최대 5개까지 가능합니다\n"
                "• 날짜 형식: YYYY-MM-DD\n"
                "예시) `/단일투표 \"레이드 날짜\" 2024-11-28 2024-12-05`"
            ),
            inline=False
        )

        embed.add_field(
            name="📊 /중복투표 [제목] [날짜]",
            value=(
                "중복 투표를 생성합니다.\n"
                "• 제목은 큰따옴표(\")로 감싸주세요!\n"
                "• 날짜는 최대 5개까지 가능합니다\n"
                "• 날짜 형식: YYYY-MM-DD\n"
                "예시) `/중복투표 \"레이드 가능한 날짜\" 2024-11-28 2024-12-05`"
            ),
            inline=False
        )

        embed.add_field(
            name="📝 /투표목록",
            value=(
                "현재 진행 중인 모든 투표 목록을 표시합니다.\n"
                "예시) `/투표목록`"
            ),
            inline=False
        )

        embed.add_field(
            name="🔒 /투표종료 [제목]",
            value=(
                "진행 중인 투표를 종료합니다.\n"
                "예시) `/투표종료 레이드 날짜"
            ),
            inline=False
        )

        embed.set_footer(text="💡 자세한 내용은 개발자에게 문의해주세요!")
        await ctx.send(embed=embed)

    @help_command.command(name='보스')
    async def help_boss(self, ctx):
        """보스 공략 도움말"""
        embed = discord.Embed(
            title="🗡️ 보스 공략 명령어 도움말",
            description="보스 공략 관련 명령어 목록입니다.",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="/보스, /boss, /b",
            value=(
                "전체 보스 목록을 확인합니다.\n"
                "예시) `/보스 [보스이름]`"
            ),
            inline=False
        )

        embed.add_field(
            name=RAID_CATEGORIES[0],  # 군단장 레이드
            value=(
                "• `/보스 발탄` - 마수군단장\n"
                "• `/보스 비아키스` - 욕망군단장\n"
                "• `/보스 쿠크세이튼` - 광기군단장\n"
                "• `/보스 아브렐슈드` - 몽환군단장\n"
                "• `/보스 일리아칸` - 질병군단장\n"
                "• `/보스 카멘` - 어둠군단장"
            ),
            inline=False
        )

        embed.add_field(
            name=RAID_CATEGORIES[1],  # 에픽 레이드
            value="• `/보스 베히모스` - 폭풍의 지휘관",
            inline=False
        )

        embed.add_field(
            name=RAID_CATEGORIES[2],  # 어비스 레이드
            value=(
                "• `/보스 카양겔` - 영원한 빛의 요람\n"
                "• `/보스 상아탑` - 짓밟힌 정원"
            ),
            inline=False
        )

        embed.add_field(
            name=RAID_CATEGORIES[3],  # 카제로스 레이드
            value=(
                "• `/보스 에키드나` - 서막 : 붉어진 백야의 나선\n"
                "• `/보스 에기르` - 1막 : 대지를 부수는 업화의 궤적\n"
                "• `/보스 진아브렐슈드` - 2막 : 부유하는 악몽의 진혼곡\n"
                "• `/보스 모르둠` - 3막 : 칠흑, 폭풍의 밤"
            ),
            inline=False
        )

        embed.set_footer(text="💡 각 보스의 상세 공략을 보려면 해당 명령어를 입력하세요.")
        await ctx.send(embed=embed)


async def setup(bot):
    """Cog 등록"""
    await bot.add_cog(HelpCog(bot))
