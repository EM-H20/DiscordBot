#====================================공지사항 Cog======================================
# 로스트아크 공지사항 관련 명령어들을 관리합니다.

import discord
from discord.ext import commands
from config import LOSTARK_NOTICE_URL, BANNER_IMAGE_PATH


class NoticeCog(commands.Cog):
    """공지사항 명령어 Cog"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='공지사항', aliases=['notice'])
    async def notice(self, ctx):
        """로스트아크 공지사항 링크 전송"""
        await self.send_notice(ctx.channel)

    async def send_notice(self, channel=None):
        """
        공지사항을 특정 채널에 전송합니다.
        :param channel: 전송할 채널 (None이면 설정된 CHANNEL_ID 사용)
        """
        from data import CHANNEL_ID

        try:
            # 채널이 지정되지 않은 경우 기본 채널 사용
            if channel is None:
                channel = await self.bot.fetch_channel(CHANNEL_ID)

            embed = discord.Embed(
                title="🔔 공지사항",
                description="현재까지 올라온 공지내용입니다!",
                color=discord.Color.purple()
            )
            embed.add_field(
                name="ヾ(•ω•`)o",
                value=LOSTARK_NOTICE_URL,
                inline=False
            )

            files = [
                discord.File(BANNER_IMAGE_PATH, filename="banner.png"),
            ]

            embed.set_image(url="attachment://banner.png")
            embed.set_footer(text="💡 자세한 내용은 개발자에게 문의해주세요!")
            await channel.send(file=files[0], embed=embed)

        except discord.NotFound:
            print(f"Channel with ID {CHANNEL_ID} not found.")
        except discord.Forbidden:
            print("Bot does not have permission to access this channel.")
        except discord.HTTPException as e:
            print(f"An error occurred while trying to access the channel: {e}")


async def setup(bot):
    """Cog 등록"""
    await bot.add_cog(NoticeCog(bot))
