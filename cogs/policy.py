#====================================정책사항 Cog======================================
# 정책사항, 서비스약관, 개인정보처리방침 관련 명령어들을 관리합니다.

import discord
from discord.ext import commands
from config import TERMS_OF_SERVICE_URL, PRIVACY_POLICY_URL


class PolicyCog(commands.Cog):
    """정책사항 명령어 Cog"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='정책사항', aliases=['policy'])
    async def policy(self, ctx):
        """정책사항, 서비스약관, 개인정보처리방침 링크를 보여줍니다."""
        embed = discord.Embed(
            title="📜 정책 사항",
            description="아래 링크에서 서비스약관 및 개인정보처리방침을 확인하실 수 있습니다.",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="서비스약관 링크",
            value=f"[확인하기]({TERMS_OF_SERVICE_URL})",
            inline=False
        )
        embed.add_field(
            name="개인정보처리방침 링크",
            value=f"[확인하기]({PRIVACY_POLICY_URL})",
            inline=False
        )

        await ctx.send(embed=embed)


async def setup(bot):
    """Cog 등록"""
    await bot.add_cog(PolicyCog(bot))
