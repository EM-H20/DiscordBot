#====================================챗봇 Cog======================================
# Gemini AI 챗봇 관련 명령어들을 관리합니다.

import discord
from discord.ext import commands
import google.generativeai as genai
from data import GEMINI_API_KEY


# Gemini API 설정
genai.configure(api_key=GEMINI_API_KEY)


class ChatBotCog(commands.Cog):
    """Gemini AI 챗봇 Cog"""

    def __init__(self, bot):
        self.bot = bot
        self.model = genai.GenerativeModel('gemini-pro')
        self.chat = self.model.start_chat(history=[])

    @commands.command(name='질문', aliases=['ask', 'gemini', 'g'])
    async def ask(self, ctx, *, question):
        """
        Gemini AI에게 질문하기
        :param ctx: 명령어 컨텍스트
        :param question: 질문 내용
        """
        try:
            loading_msg = await ctx.send("🤔 답변을 생성하고 있습니다...")

            # Gemini API 호출
            response = await self.chat.send_message_async(question)
            answer = response.text

            embed = discord.Embed(
                title="🤖 Gemini 답변",
                description=answer,
                color=discord.Color.blue()
            )
            embed.add_field(name="질문", value=question, inline=False)

            await loading_msg.delete()
            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"오류가 발생했습니다: {e}")
            print(f"Gemini Error: {e}")

    @ask.error
    async def ask_error(self, ctx, error):
        """질문 명령어 오류 처리"""
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("질문 내용을 입력해주세요! 예시: `/질문 파이썬이란?`")


async def setup(bot):
    """Cog 등록"""
    await bot.add_cog(ChatBotCog(bot))
