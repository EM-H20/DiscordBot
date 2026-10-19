#====================================관리 명령어 Cog======================================
# 봇 관리자용 명령어들을 관리합니다. (재부팅, 상태 확인 등)

import discord
from discord.ext import commands
import sys
import os


class AdminCog(commands.Cog):
    """봇 관리 명령어 Cog"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='재부팅', aliases=['reboot', 'restart'])
    @commands.is_owner()  # 봇 소유자만 사용 가능
    async def reboot(self, ctx):
        """봇 재부팅 명령어"""
        try:
            await ctx.send('봇을 재부팅합니다...')
            await self.bot.change_presence(status=discord.Status.offline)
            await self.bot.close()
            os.execv(sys.executable, ['python'] + sys.argv)
        except Exception as e:
            await ctx.send(f'재부팅 중 오류가 발생했습니다: {e}')

    @commands.command(name='상태', aliases=['status'])
    async def status(self, ctx):
        """봇 상태 확인 명령어"""
        await ctx.send(f'{ctx.author.mention}님, 봇의 상태는 {self.bot.status}입니다.')
        await ctx.author.send(f'{ctx.author.name}님, 봇의 상태는 {self.bot.status}입니다.')


async def setup(bot):
    """Cog 등록"""
    await bot.add_cog(AdminCog(bot))
