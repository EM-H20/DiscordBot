#플래닝
#====================================라이브러리 설정======================================
from bs4 import BeautifulSoup
from data import Token, GEMINI_API_KEY, CHANNEL_ID #봇 토큰, Gemini API 키
from datetime import datetime #날짜 라이브러리
from discord import ButtonStyle, SelectOption #버튼 스타일, 드롭다운 메뉴 옵션 라이브러리
from discord.ext import commands #명령어 라이브러리
from discord.ui import Button, View, Select #버튼, 뷰, 드롭다운 메뉴 라이브러리
from apscheduler.schedulers.asyncio import AsyncIOScheduler #비동기 작업을 처리하기 위한 스케줄러
from apscheduler.triggers.cron import CronTrigger #스케줄을 설정할 때 CronTrigger 사용
import google.generativeai as genai #Gemini API 라이브러리
import discord #디스코드 라이브러리
import asyncio #비동기 라이브러리
import calendar #달력 라이브러리
import json
from typing import Dict, List, Optional, Any



# Gemini API 설정
genai.configure(api_key=GEMINI_API_KEY)
intents = discord.Intents.default() # bot이 사용할 기능과 관련된 옵션
intents.message_content = True      # 사용자의 입력에 따라 작동하는 기능을 개발하기 위해 true 
bot = commands.Bot(command_prefix='/', intents=intents) #명령어 시작을 '/' 로한다 ex) /help
Boss_List = ['군단장 레이드', '에픽 레이드', '어비스 레이드', '카제로스 레이드']
schedule = AsyncIOScheduler()
#====================================봇 초기 설정======================================
@bot.event
async def on_ready():
    await setup(bot)
    print(f'{bot.user.name}이 연결되었습니다')
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("/phelp"))

    schedule.start()

#봇 재부팅 코드
@bot.command(name='재부팅', aliases=['reboot', 'restart'])
@commands.is_owner()  # 봇 소유자만 사용 가능
async def reboot(ctx):
    try:
        await ctx.send('봇을 재부팅합니다...')
        await bot.change_presence(status=discord.Status.offline)
        await bot.close()
        import sys
        import os
        os.execv(sys.executable, ['python'] + sys.argv)
    except Exception as e:
        await ctx.send(f'재부팅 중 오류가 발생했습니다: {e}')

#상태 확인 코드
@bot.command(name='상태', aliases=['status'])
async def status(ctx):
    await ctx.send(f'{ctx.author.mention}님, 봇의 상태는 {bot.status}입니다.')
    await ctx.author.send(f'{ctx.author.name}님, 봇의 상태는 {bot.status}입니다.')

#===================================[봇 관련 명령어]====================================
#====================================[봇 help 코드]======================================
@bot.group(name='phelp', aliases=['p도움말'])
async def help_command(ctx):
    """도움말 명령어"""
    if ctx.invoked_subcommand is None:  # 하위 명령어가 없는 경우
        if len(ctx.message.content.split()) > 1:  # 잘못된 카테고리가 입력된 경우
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
            await ctx.send(embed=embed)
            return

        # 기본 도움말 표시
        embed = discord.Embed(
            title="📋 도움말 카테고리",
            description="원하는 카테고리의 도움말을 보려면 `/phelp [카테고리]`를 입력하세요.",
            color=discord.Color.blue()
        )

        # 카테고리 목록 (한 번만 추가)
        embed.add_field(
            name="📜 정책사항",
            value="정책사항을 보고 싶다면 `/정책사항 or /policy`를 입력하세요.",  # 공지사항 명령어 추가
            inline=False
        )

        embed.add_field(
            name="🔔 공지사항",
            value="로스트아크 공지사항을 보고 싶다면 `/공지사항 or /notice`를 입력하세요.",  # 공지사항 명령어 추가
            inline=False
        )
        
        embed.add_field(
            name="📊 투표",
            value="투표 관련 명령어를 확인하려면 `/phelp 투표`를 입력하세요.", #투표 명령어 추가
            inline=False
        )

        embed.add_field(
            name="🤖 챗봇",
            value="Gemini AI 관련 명령어를 확인하려면 `/phelp 챗봇`를 입력하세요.",  # Gemini AI로 수정
            inline=False
        )

        embed.add_field(
            name="🏰 보스",
            value="보스 공략 명령어를 확인하려면 `/phelp 보스`를 입력하세요.", #보스 공략 명령어 추가
            inline=False
        )

        embed.set_footer(text="💡 자세한 내용은 개발자에게 문의해주세요!")
        await ctx.send(embed=embed)

@help_command.error  # help_command의 오류 처리
async def help_error(ctx, error):
    """도움말 명령어 오류 처리"""
    if isinstance(error, commands.CommandNotFound):
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
        await ctx.send(embed=embed)

# 일반적인 명령어 오류 처리
@bot.event
async def on_command_error(ctx, error):
    """일반 명령어 오류 처리"""
    if isinstance(error, commands.CommandNotFound):
        # help 명령어가 아닌 경우에만 처리
        if not ctx.message.content.startswith(('/phelp', '/p도움말')):
            await ctx.send(f"존재하지 않는 명령어입니다. 도움말을 보려면 `/phelp`를 입력하세요.")

#====================================[챗봇 명령어 help 코드]======================================
@help_command.command(name='챗봇')
async def help_Gemini(ctx):
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

#====================================[투표 명령어 help 코드]======================================
@help_command.command(name='투표')
async def help_vote(ctx):
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

#====================================[보스 명령어 help 코드]======================================
@help_command.command(name='보스')
async def help_boss(ctx):
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
        name=Boss_List[0],
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
        name=Boss_List[1],
        value=(
            "• `/보스 베히모스` - 폭풍의 지휘관"
        ),
        inline=False
    )

    embed.add_field(
        name=Boss_List[2],
        value=(
            "• `/보스 카양겔` - 영원한 빛의 요람\n"
            "• `/보스 상아탑` - 짓밟힌 정원"
        ),
        inline=False
    )

    embed.add_field(
        name=Boss_List[3],
        value=(
            "• `/보스 에키드나` - 서막 : 붉어진 백야의 나선\n"
            "• `/보스 에기르` - 1막 : 대지를 부수는 업화의 궤적\n"
            "• `/보스 진아브렐슈드` - 2막 : 부유하는 악몽의 진혼곡"
        ),
        inline=False
    )

    embed.set_footer(text="💡 각 보스의 상세 공략을 보려면 해당 명령어를 입력하세요.")
    await ctx.send(embed=embed)

#===================================[공지사항 명령어]=====================================
Discord_Channel = bot.get_channel(CHANNEL_ID)
LostArkNotice_URL = "https://lostark.game.onstove.com/News/Notice/List"

@bot.command(name='공지사항', aliases=['notice'])
async def LostArkNotice(ctx):
    await send_LostArkNotice()

async def send_LostArkNotice():
    try:
        Discord_Channel = await bot.fetch_channel(CHANNEL_ID)  # fetch_channel() 사용
        embed = discord.Embed(
            title="🔔 공지사항",
            description="현재까지 올라온 공지내용입니다!",
            color=discord.Color.purple()
        )
        embed.add_field(
            name="ヾ(•ω•`)o",
            value=LostArkNotice_URL,
            inline=False
        )
           
        files = [
            discord.File("images/banner/banner_share.png", filename="banner.png"),
        ]
        
        embed.set_image(url="attachment://banner.png")
        await Discord_Channel.send(file=files[0], embed=embed)
        embed.set_footer(text="💡 자세한 내용은 개발자에게 문의해주세요!")

    except discord.NotFound:
        print(f"Channel with ID {CHANNEL_ID} not found.")
    except discord.Forbidden:
        print("Bot does not have permission to access this channel.")
    except discord.HTTPException:
        print("An error occurred while trying to access the channel.")
    

#===================================[정책사항 명령어]===================================

class PolicyCog(commands.Cog):
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
        # 실제 정책사항, 서비스약관, 개인정보처리방침 링크로 변경해주세요.
        Terms_of_Service = "https://gist.github.com/EM-H20/3d980bb67316ba4f8836650af9630285"  # 서비스약관 링크
        Privacy_Policy = "https://gist.github.com/EM-H20/6aaefdaa5c5a15fcbcbb36131aa764aa" # 개인정보처리방침 링크

        embed.add_field(name="서비스약관 링크", value=f"[확인하기]({Terms_of_Service})", inline=False)
        embed.add_field(name="개인정보처리방침 링크", value=f"[확인하기]({Privacy_Policy})", inline=False)

        await ctx.send(embed=embed)

#====================================[챗봇 명령어]======================================
class ChatBot(commands.Cog):  
    def __init__(self, bot): 
        self.bot = bot #봇 객체
        self.model = genai.GenerativeModel('gemini-pro') #Gemini API 모델
        self.chat = self.model.start_chat(history=[]) #Gemini API 챗봇

    @commands.command(name='질문', aliases=['ask', 'gemini', 'g']) 
    async def ask(self, ctx, *, question): #매개변수 : 채널, 질문
        """Gemini에게 질문하기"""
        try:
            loading_msg = await ctx.send("🤔 답변을 생성하고 있습니다...") #로딩 메시지

            # Gemini API 호출
            response = await self.chat.send_message_async(question)
            answer = response.text

            embed = discord.Embed( #답변 표시
                title="🤖 Gemini 답변",
                description=answer,
                color=discord.Color.blue()
            )
            embed.add_field(name="질문", value=question, inline=False)

            await loading_msg.delete() #로딩 메시지 삭제
            await ctx.send(embed=embed) #답변 표시  

        except Exception as e:
            await ctx.send(f"오류가 발생했습니다: {e}")
            print(f"Gemini Error: {e}")

#====================================[일정 투표 명령어]======================================
class DateSelect(Select):
    def __init__(self, dates):
        options = []
        for date in dates:
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            weekday = ['월', '화', '수', '목', '금', '토', '일'][date_obj.weekday()]
            options.append(
                SelectOption(
                    label=f"{date_obj.month}월 {date_obj.day}일 ({weekday})", # 날짜 표시
                    value=date,
                    description=f"{date_obj.year}년 {date_obj.month}월 {date_obj.day}일"
                )
            )
        
        super().__init__(
            placeholder="날짜를 선택하세요", # 날짜 선택 표시
            min_values=1, # 최소 날짜 선택 개수
            max_values=1, # 최대 날짜 선택 개수
            options=options
        )
        self.votes = {} # 투표 데이터

    async def callback(self, interaction): # 투표 콜백 함수
        user_id = interaction.user.id # 유저 아이디
        selected_date = self.values[0] # 선택한 날짜
        
        if user_id in self.votes: # 이전 투표 날짜 존재 여부
            old_vote = self.votes[user_id] # 이전 투표 날짜
            if old_vote == selected_date: # 이전 투표 날짜와 동일한 경우
                await interaction.response.send_message("이미 선택한 날짜입니다!", ephemeral=True)
                return
        
        self.votes[user_id] = selected_date # 투표 데이터 저장
        
        await interaction.response.send_message(f"'{selected_date}'에 투표하셨습니다!", ephemeral=True) # 투표 완료 메시지
        try:
            date_obj = datetime.strptime(selected_date, '%Y-%m-%d')
            weekday = ['월', '화', '수', '목', '금', '토', '일'][date_obj.weekday()]
            await interaction.user.send(
                f"📊 단일투표 알림\n"
                f"{interaction.message.embeds[0].title}에서\n"
                f"{date_obj.month}월 {date_obj.day}일 ({weekday})에 투표하셨습니다!"
            )
        except discord.Forbidden:
            pass

        vote_counts = {} # 투표 데이터
        for date in self.votes.values():
            vote_counts[date] = vote_counts.get(date, 0) + 1 # 투표 데이터 저장
        
        embed = interaction.message.embeds[0] # 투표 데이터
        embed.clear_fields()
        
        total_votes = len(self.votes) # 총 투표 수
        max_votes = max(vote_counts.values()) if vote_counts else 0 # 최대 투표 수
        
        sorted_dates = sorted(vote_counts.items(), key=lambda x: x[1], reverse=True) # 정렬
        
        for date, count in sorted_dates:
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            weekday = ['월', '화', '수', '목', '금', '토', '일'][date_obj.weekday()]
            percentage = (count / total_votes * 100) if total_votes > 0 else 0
            
            bar = "🟦" * round(count/max_votes * 10) + "⬜" * (10 - round(count/max_votes * 10)) # 바 표시
            
            embed.add_field(
                name=f"{date_obj.month}월 {date_obj.day}일 ({weekday})",
                value=f"{bar} {count}명 ({percentage:.1f}%)",
                inline=False
            )
        
        await interaction.message.edit(embed=embed) # 투표 데이터 수정

class PollView(View): #투표 뷰
    def __init__(self, dates):
        super().__init__(timeout=None) # 타임아웃 없음
        self.date_select = DateSelect(dates) # 날짜 선택
        self.add_item(self.date_select) # 날짜 선택 아이템 추가

class Schedule(commands.Cog): #일정 투표 명령어
    def __init__(self, bot):
        self.bot = bot
        self.active_polls = {} # 투표 데이터

    @commands.command(name='단일투표') #단일 투표 명령어
    async def create_poll(self, ctx, title=None, *dates):
        if title is None: # 투표 제목 없는 경우
            await ctx.send("투표 제목을 입력해주세요!")
            return

        if len(dates) == 0:
            await ctx.send("날짜를 최소 1개 이상 입력해주세요!")
            return

        if len(dates) > 5:
            await ctx.send("최대 5개까지의 날짜만 선택 가능합니다!")
            return

        try:
            for date in dates:
                datetime.strptime(date, '%Y-%m-%d') # 날짜 형식 올바른지 확인
        except ValueError:
            await ctx.send("날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식으로 입력해주세요.")
            return

        embed = discord.Embed(
            title=f"📅 {title}",
            description="아래 드롭다운 메뉴에서 선호하는 날짜를 선택해주세요.",
            color=discord.Color.blue()
        )

        view = PollView(dates) # 투표 뷰
        message = await ctx.send(embed=embed, view=view) # 투표 메시지
        self.active_polls[message.id] = view.date_select # 투표 데이터 저장

    @commands.command(name='투표종료') # 투표 종료 명령어
    async def end_poll(self, ctx, *, title=None):
        try:
            if title is None: # 투표 제목 없는 경우
                await ctx.send("투표 제목을 입력해주세요! 투표 목록을 보려면 `/투표목록`을 입력하세요.")
                return

            found_polls = []
            async for message in ctx.channel.history(limit=100): # 투표 메시지 존재 여부
                if message.embeds and message.id in self.active_polls: # 투표 데이터 존재 여부
                    message_title = message.embeds[0].title.replace("📅 ", "").strip() # 투표 제목
                    if message_title == title:
                        date_select = self.active_polls.get(message.id) # 투표 데이터
                        if not date_select:
                            continue
                        poll_type = "중복" if isinstance(date_select, MultiDateSelect) else "단일" # 투표 타입
                        found_polls.append((message, poll_type))

            if not found_polls: # 투표 데이터 없는 경우
                await ctx.send(f"'{title}' 제목의 진행 중인 투표를 찾을 수 없습니다.")
                return

            if len(found_polls) > 1: # 여러 개의 투표 데이터 존재 여부
                select_embed = discord.Embed(
                    title=f"📊 '{title}' 투표 선택",
                    description="종료하려는 투표의 번호를 입력해주세요. (예: 1)",
                    color=discord.Color.blue()
                )
                
                for i, (msg, poll_type) in enumerate(found_polls, 1):
                    vote_count = len(self.active_polls[msg.id].votes) # 투표 수
                    select_embed.add_field(
                        name=f"{i}. {title} ({poll_type}투표)",
                        value=f"현재 {vote_count}명 참여 중",
                        inline=False
                    )
                
                await ctx.send(embed=select_embed)
                
                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit() # 메시지 체크
                
                try:
                    msg = await self.bot.wait_for('message', check=check, timeout=30.0) # 메시지 대기
                    selection = int(msg.content) # 선택한 번호
                    if 1 <= selection <= len(found_polls): # 번호 범위 체크
                        message, poll_type = found_polls[selection-1] # 투표 데이터
                    else:
                        await ctx.send("올바른 번호를 입력해주세요.")
                        return
                except asyncio.TimeoutError: # 시간 초과 체크
                    await ctx.send("시간이 초과되었습니다. 다시 시도해주세요.")
                    return
                except ValueError: # 숫자 체크
                    await ctx.send("올바른 번호를 입력해주세요.")
                    return
            else:
                message, poll_type = found_polls[0] # 투표 데이터

            date_select = self.active_polls.get(message.id) # 투표 데이터
            if not date_select: # 투표 데이터 없는 경우
                await ctx.send("투표 데이터를 찾을 수 없습니다.")
                return
            
            if not date_select.votes: # 투표 없는 경우
                await ctx.send("아직 투표가 없습니다.")
                return

            vote_counts = {} # 투표 데이터
            if isinstance(date_select, MultiDateSelect): # 중복 투표 여부
                for user_votes in date_select.votes.values():
                    for date in user_votes:
                        vote_counts[date] = vote_counts.get(date, 0) + 1 # 투표 데이터 저장
                total_votes = sum(vote_counts.values()) # 총 투표 수
            else:
                for date in date_select.votes.values():
                    vote_counts[date] = vote_counts.get(date, 0) + 1 # 투표 데이터 저장
                total_votes = len(date_select.votes) # 총 투표 수

            result_embed = discord.Embed(
                title=f"📊 투표 결과: {title}",
                description=f"총 투표 수: {total_votes}명 ({poll_type}투표)",
                color=discord.Color.green()
            )

            sorted_results = sorted(vote_counts.items(), key=lambda x: x[1], reverse=True)
            if sorted_results: # 투표 데이터 존재 여부
                max_votes = sorted_results[0][1] # 최대 투표 수

                for date, count in sorted_results:
                    date_obj = datetime.strptime(date, '%Y-%m-%d') # 날짜 형식 올바른지 확인
                    weekday = ['월', '화', '수', '목', '금', '토', '일'][date_obj.weekday()] # 요일 확인
                    percentage = (count / total_votes * 100) # 투표 비율
                    
                    bar = "🟦" * round(count/max_votes * 10) + "⬜" * (10 - round(count/max_votes * 10)) # 바 표시
                    
                    result_embed.add_field(
                        name=f"{date_obj.month}월 {date_obj.day}일 ({weekday})",
                        value=f"{bar} {count}명 ({percentage:.1f}%)",
                        inline=False
                    )

                winners = [date for date, votes in sorted_results if votes == max_votes] # 최다 선택된 날짜
                if len(winners) == 1: # 최다 선택된 날짜 1개인 경우
                    date_obj = datetime.strptime(winners[0], '%Y-%m-%d') # 날짜 형식 올바른지 확인
                    weekday = ['월', '화', '수', '목', '금', '토', '일'][date_obj.weekday()]
                    result_embed.set_footer(text=f"✨ 최다 선택된 날짜: {date_obj.month}월 {date_obj.day}일 ({weekday})")
                else: # 최다 선택된 날짜 여러 개인 경우
                    winner_texts = []
                    for date in winners:
                        date_obj = datetime.strptime(date, '%Y-%m-%d') # 날짜 형식 올바른지 확인
                        weekday = ['월', '화', '수', '목', '금', '토', '일'][date_obj.weekday()]
                        winner_texts.append(f"{date_obj.month}월 {date_obj.day}일 ({weekday})")
                    result_embed.set_footer(text=f"✨ 최다 선택된 날짜들: {', '.join(winner_texts)}")

            voters = set() # 투표자 데이터
            if isinstance(date_select, MultiDateSelect):
                voters = set(date_select.votes.keys())
            else:
                voters = set(date_select.votes.keys())

            if voters: # 투표자 데이터 존재 여부
                date_voters = {} # 날짜별 투표자 데이터
                if isinstance(date_select, MultiDateSelect): # 중복 투표 여부
                    for user_id, dates in date_select.votes.items(): # 투표자 데이터
                        for date in dates:
                            if date not in date_voters:
                                date_voters[date] = []
                            date_voters[date].append(user_id)
                else:
                    for user_id, date in date_select.votes.items(): # 투표자 데이터
                        if date not in date_voters:
                            date_voters[date] = []
                        date_voters[date].append(user_id)
                
                result_embed.add_field(
                    name="📢 날짜별 투표 참여자",
                    value="\n".join(
                        f"{date_obj.month}월 {date_obj.day}일 ({weekday}): " + 
                        " ".join(f"<@{user_id}>" for user_id in date_voters.get(date, []))
                        for date, date_obj, weekday in [
                            (date, datetime.strptime(date, '%Y-%m-%d'), 
                             ['월', '화', '수', '목', '금', '토', '일'][datetime.strptime(date, '%Y-%m-%d').weekday()])
                            for date in sorted(date_voters.keys())
                        ]
                    ),
                    inline=False
                )

            await ctx.send(embed=result_embed) # 투표 결과 메시지

            new_embed = message.embeds[0]
            new_embed.description = "🔒 투표가 종료되었습니다."
            await message.edit(embed=new_embed, view=None)
            
            del self.active_polls[message.id]

        except discord.NotFound: # 메시지 없는 경우
            await ctx.send("메시지를 찾을 수 없습니다.")
        except discord.Forbidden: # 권한 없는 경우
            await ctx.send("메시지를 수정할 권한이 없습니다.")
        except Exception as e: # 오류 체크
            await ctx.send(f"오류가 발생했습니다: {e}")
            print(f"Error in end_poll: {e}")

    @commands.command(name='투표목록') # 투표 목록 명령어
    async def list_polls(self, ctx):
        if not self.active_polls: # 투표 데이터 없는 경우
            await ctx.send("진행 중인 투표가 없습니다.")
            return

        try:
            messages = {msg.id: msg async for msg in ctx.channel.history(limit=100)} # 투표 메시지
            
            to_remove = [msg_id for msg_id in self.active_polls if msg_id not in messages] # 투표 데이터 삭제
            for msg_id in to_remove:
                del self.active_polls[msg_id] # 투표 데이터 삭제

            if not self.active_polls: # 투표 데이터 없는 경우
                await ctx.send("진행 중인 투표가 없습니다.")
                return

            embed = discord.Embed(
                title="📋 진행 중 투표 목록",
                description="투표를 종료하려면 `/투표종료 [제목]을 입력하세요.",
                color=discord.Color.blue()
            )

            for msg_id, date_select in self.active_polls.items(): # 투표 데이터
                if msg_id in messages: # 투표 메시지 존재 여부
                    message = messages[msg_id] # 투표 메시지
                    if message.embeds: # 투표 데이터 존재 여부
                        title = message.embeds[0].title.replace("📅 ", "") # 투표 제목
                        vote_count = len(date_select.votes) # 투표 수
                        poll_type = "중복" if isinstance(date_select, MultiDateSelect) else "단일" # 투표 타입
                        embed.add_field(
                            name=f"📊 {title}",
                            value=f"현재 {vote_count}명 참여 중 ({poll_type}투표)",
                            inline=False
                        )

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"투표 목록을 가져오는 중 오류가 발생했습니다: {e}")

    @commands.command(name='중복투표') # 중복 투표 명령어
    async def create_multi_poll(self, ctx, title=None, *dates):
        if title is None: # 투표 제목 없는 경우
            await ctx.send("투표 제목을 입력해주세요!") 
            return

        if len(dates) == 0: # 날짜 없는 경우
            await ctx.send("날짜를 최소 1개 이상 입력해주세요!")
            return

        if len(dates) > 5: # 날짜 5개 초과 경우
            await ctx.send("최대 5개까지의 날짜만 선택 가능합니다!")
            return

        try:
            for date in dates:
                datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            await ctx.send("날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식으로 입력해주세요.")
            return

        embed = discord.Embed(
            title=f"📅 {title}",
            description="아래 드롭다운 메뉴에서 가능한 날짜를 모두 선택해주세요.",
            color=discord.Color.blue()
        )

        view = MultiPollView(dates) # 중복 투표 명령어
        message = await ctx.send(embed=embed, view=view)
        self.active_polls[message.id] = view.date_select # 투표 데이터 저장

class MultiDateSelect(Select): # 중복 투표 명령어
    def __init__(self, dates):
        options = []
        for date in dates:
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            weekday = ['월', '화', '수', '목', '금', '토', '일'][date_obj.weekday()]
            options.append(
                SelectOption(
                    label=f"{date_obj.month}월 {date_obj.day}일 ({weekday})",
                    value=date,
                    description=f"{date_obj.year}년 {date_obj.month}월 {date_obj.day}일"
                )
            )
        
        super().__init__(
            placeholder="날짜를 선택하세요 (여러 개 선택 가능)",
            min_values=1,
            max_values=len(dates),
            options=options
        )
        self.votes = {}

    async def callback(self, interaction):
        user_id = interaction.user.id
        selected_dates = self.values
        
        if user_id in self.votes and set(self.votes[user_id]) == set(selected_dates):
            await interaction.response.send_message("이미 동일한 날짜들을 선택하셨습니다!", ephemeral=True)
            return
        
        self.votes[user_id] = selected_dates
        
        await interaction.response.send_message(
            f"선택한 날짜: {', '.join(selected_dates)}에 투표하셨습니다!", 
            ephemeral=True
        )
        
        try:
            dm_message = f"📊 중복투표 알림\n{interaction.message.embeds[0].title}에서\n선택하신 날짜:\n"
            for date in selected_dates:
                date_obj = datetime.strptime(date, '%Y-%m-%d')
                weekday = ['월', '화', '수', '목', '금', '토', '일'][date_obj.weekday()]
                dm_message += f"• {date_obj.month}월 {date_obj.day}일 ({weekday})\n"
            
            await interaction.user.send(dm_message)
        except discord.Forbidden:
            pass
        
        vote_counts = {}
        for user_votes in self.votes.values():
            for date in user_votes:
                vote_counts[date] = vote_counts.get(date, 0) + 1
        
        embed = interaction.message.embeds[0]
        embed.clear_fields()
        
        total_votes = sum(vote_counts.values())
        max_votes = max(vote_counts.values()) if vote_counts else 0
        
        sorted_dates = sorted(vote_counts.items(), key=lambda x: x[1], reverse=True)
        
        for date, count in sorted_dates:
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            weekday = ['월', '화', '수', '목', '금', '토', '일'][date_obj.weekday()]
            percentage = (count / total_votes * 100)
            
            bar = "🟦" * round(count/max_votes * 10) + "⬜" * (10 - round(count/max_votes * 10))
            
            embed.add_field(
                name=f"{date_obj.month}월 {date_obj.day}일 ({weekday})",
                value=f"{bar} {count}명 ({percentage:.1f}%)",
                inline=False
            )
        
        await interaction.message.edit(embed=embed)

#====================================[중복 투표 명령어]======================================
class MultiPollView(View):
    def __init__(self, dates):
        super().__init__(timeout=None)
        self.date_select = MultiDateSelect(dates) # 중복 투표 명령어
        self.add_item(self.date_select)

#====================================[보스 공략 명령어]======================================


class BossStrategy(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.boss_data: Dict[str, Any] = self._load_boss_data() # 보스 데이터 로드

    def _load_boss_data(self) -> Dict[str, Any]:
        """
        JSON 파일에서 보스 데이터를 로드합니다.
        :return: 보스 정보를 담은 딕셔너리
        """
        with open('boss_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data['bosses']
    
    async def _send_embed(self, ctx: commands.Context, embed: discord.Embed, files: Optional[List[discord.File]] = None):
         """
        임베드와 파일을 전송하는 함수
        :param ctx: discord.ext.commands.Context 객체 (명령어 컨텍스트)
        :param embed: discord.Embed 객체 (전송할 임베드)
        :param files: Optional[List[discord.File]] 객체 (전송할 파일 리스트)
        """
         if files:
            await ctx.send(embed=embed)
            await asyncio.sleep(0.1)  # 0.5초 딜레이
            await ctx.send(file=files[0])
         else:
           await ctx.send(embed=embed)


    async def _send_boss_selection(self, ctx: commands.Context, boss_name: str):
        """
        보스 선택 임베드 메시지를 보내고 난이도 선택을 처리
        :param ctx: discord.ext.commands.Context 객체 (명령어 컨텍스트)
        :param boss_name: str (보스 이름)
        """
        boss_info = self.boss_data.get(boss_name)
        if not boss_info:
            await ctx.send("해당 보스 정보가 없습니다.")
            return

        embed = discord.Embed(
            title=f"⚔️ {boss_name} 공략 정보 선택",
            description="난이도를 선택하세요.",
            color=discord.Color.gold()
        )
        
        emojis = ['🇳' if d == '노말' else '🇭' for d in boss_info['difficulties']] # 보스 난이도에 따른 이모지 생성
        emoji_str = ' '.join([f"{e} : {'노말' if e == '🇳' else '하드'}" for e in emojis]) # 이모지를 문자열로 변환
        embed.add_field(
            name="난이도 선택",
            value=emoji_str,
            inline=False
        )
        
        msg = await ctx.send(embed=embed) # 임베드 메시지 전송
        for emoji in emojis:  # 모든 난이도 이모티콘에 대한 반응 추가
            await msg.add_reaction(emoji) # 메시지에 난이도 이모티콘 추가

        def check(reaction: discord.Reaction, user: discord.User) -> bool:
            """
            반응 확인 함수
            :param reaction: discord.Reaction 객체 (반응)
            :param user: discord.User 객체 (반응한 사용자)
            :return: bool (반응 조건 충족 여부)
            """
            return user == ctx.author and str(reaction.emoji) in emojis and reaction.message.id == msg.id # 반응한 사용자가 명령어 사용자, 이모티콘이 난이도 이모티콘 중 하나, 반응한 메시지가 현재 메시지인지 확인
        
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=10.0, check=check) # 반응 대기 (10초 제한)
            selected_difficulty = '노말' if str(reaction.emoji) == '🇳' else '하드'
            await self._show_difficulty_info(ctx, boss_name, selected_difficulty) # 선택된 난이도 정보 표시 함수 호출
        except asyncio.TimeoutError: # 시간 초과 예외 처리
            await msg.delete() # 시간 초과 시 메시지 삭제

        await msg.delete()  # 반응 선택 후 메시지 삭제

    async def _show_difficulty_info(self, ctx: commands.Context, boss_name: str, difficulty: str):
        """
        선택된 난이도에 맞는 보스 공략 정보 표시
        :param ctx: discord.ext.commands.Context 객체 (명령어 컨텍스트)
        :param boss_name: str (보스 이름)
        :param difficulty: str (난이도)
        """
        boss_info = self.boss_data.get(boss_name)
        if not boss_info:
            await ctx.send("해당 보스 정보가 없습니다.")
            return
       
        difficulty_path = 'normal' if difficulty=='노말' else 'hard' # 난이도별 폴더 경로 설정
        
        if boss_info['gate_count'].get(difficulty, 0) > 0 :
          for i in range(1, boss_info['gate_count'][difficulty] + 1):
             file_path = f"{boss_info['image_path']}/{difficulty_path}/{i}gate.png"  # 이미지 파일 경로 생성
             try: # 이미지 파일이 있는지 확인
               file = discord.File(file_path, filename=f"{boss_name.lower()}{i}.png") # 이미지 파일 생성
               
               embed = discord.Embed(
                    title=f"⚔️ {boss_info['name']} 공략 ({difficulty}) - {boss_info['description']}",
                    description=f"{i}번 공략\n난이도: {boss_info['difficulty_stars'][difficulty]}",
                    color=getattr(discord.Color, boss_info['color'])()
                )
               await self._send_embed(ctx, embed, [file])
             except FileNotFoundError: # 파일이 없을경우 오류 출력
                await ctx.send(f"오류: `{file_path}` 파일이 없습니다.")
                return
        else:
          await ctx.send("해당 난이도에 대한 정보가 없습니다.")
          return

    @commands.group(name='보스', aliases=['boss', 'b'])
    async def boss(self, ctx: commands.Context):
        """보스 공략 명령어 그룹"""
        if ctx.invoked_subcommand is None:
            if len(ctx.message.content.split()) > 1:
                embed = discord.Embed(
                    title="❌ 오류",
                    description="존재하지 않는 보스입니다.",
                    color=discord.Color.red()
                )
                
                # 보스 목록을 추가하기 위해 설정 파일에서 데이터를 읽어옴
                for category, bosses in self._group_bosses().items():
                   boss_list = "\n• ".join([f"`/보스 {boss}` - {self.boss_data[boss]['description']}" for boss in bosses])
                   embed.add_field(name=category, value=f"• {boss_list}", inline=False)
                embed.set_footer(text="💡 전체 보스 목록을 보려면 /보스를 입력하세요.")
                await self._send_embed(ctx, embed) # 오류 임베드 전송
                return

            # 기본 보스 목록 표시
            embed = discord.Embed(
                title="🗡️ 로스트아크 레이드 공략",
                description="원하는 보스의 공략을 보려면 `/보스 [보스이름]`을 입력하세요.",
                color=discord.Color.blue()
            )

            for category, bosses in self._group_bosses().items():
               for boss in bosses:
                    embed.add_field(name=f"{boss} ({self.boss_data[boss]['name']})", value=f"`/보스 {boss}` - {self.boss_data[boss]['description']}", inline=True)

            embed.set_footer(text="💡 각 보스의 상세 공략을 보려면 해당 명령어를 입력하세요.")
            await self._send_embed(ctx, embed)
    
    def _group_bosses(self) -> Dict[str, List[str]]:
      """보스 정보를 종류별로 묶어 반환"""
      bosses = {
          '군단장 레이드': [],
          '에픽 레이드': [],
          '어비스 레이드': [],
          '카제로스 레이드': []
      }
      
      for boss_name, boss_info in self.boss_data.items():
            if '군단장' in boss_info['description']:
              bosses['군단장 레이드'].append(boss_name)
            elif '지휘관' in boss_info['description']:
              bosses['에픽 레이드'].append(boss_name)
            elif '요람' in boss_info['description'] or '정원' in boss_info['description']:
                bosses['어비스 레이드'].append(boss_name)
            elif '막' in boss_info['description'] or '서막' in boss_info['description']:
                bosses['카제로스 레이드'].append(boss_name)
      return bosses
            
    @boss.command(name='발탄')
    async def valtan(self, ctx: commands.Context, difficulty: Optional[str] = None):
        """발탄 공략 명령어"""
        await self._handle_boss_command(ctx, '발탄', difficulty)

    @boss.command(name='비아키스', aliases=['비아'])
    async def vykas(self, ctx: commands.Context, difficulty: Optional[str] = None):
        """비아키스 공략"""
        await self._handle_boss_command(ctx, '비아키스', difficulty)

    @boss.command(name='쿠크세이튼', aliases=['쿠크'])
    async def kouku(self, ctx: commands.Context, difficulty: Optional[str] = None):
        """쿠크세이튼 공략"""
        await self._handle_boss_command(ctx, '쿠크세이튼', difficulty)

    @boss.command(name='아브렐슈드', aliases=['아브'])
    async def abrelshud(self, ctx: commands.Context, difficulty: Optional[str] = None):
        """아브렐슈드 공략"""
        await self._handle_boss_command(ctx, '아브렐슈드', difficulty)

    @boss.command(name='일리아칸', aliases=['일리', '아칸'])
    async def illakan(self, ctx: commands.Context, difficulty: Optional[str] = None):
        """일리아칸 공략"""
        await self._handle_boss_command(ctx, '일리아칸', difficulty)

    @boss.command(name='카멘')
    async def kamen(self, ctx: commands.Context, difficulty: Optional[str] = None):
       """카멘 공략"""
       await self._handle_boss_command(ctx, '카멘', difficulty)

    @boss.command(name='베히모스', aliases=['베히'])
    async def behimos(self, ctx: commands.Context, difficulty: Optional[str] = None):
        """베히모스 공략"""
        await self._handle_boss_command(ctx, '베히모스', difficulty)

    @boss.command(name='카양겔', aliases=['양겔'])
    async def kayangel(self, ctx: commands.Context, difficulty: Optional[str] = None):
        """카양겔 공략"""
        await self._handle_boss_command(ctx, '카양겔', difficulty)

    @boss.command(name='상아탑', aliases=['탑'])
    async def tower(self, ctx: commands.Context, difficulty: Optional[str] = None):
        """상아탑 공략"""
        await self._handle_boss_command(ctx, '상아탑', difficulty)

    @boss.command(name='에키드나', aliases=['에키'])
    async def ekidna(self, ctx: commands.Context, difficulty: Optional[str] = None):
        """에키드나 공략"""
        await self._handle_boss_command(ctx, '에키드나', difficulty)

    @boss.command(name='에기르', aliases=['에기', '기르'])
    async def aegir1(self, ctx: commands.Context, difficulty: Optional[str] = None):
        """에기르 공략"""
        await self._handle_boss_command(ctx, '에기르', difficulty)

    @boss.command(name='진아브렐슈드', aliases=['진아브'])
    async def abrel(self, ctx: commands.Context, difficulty: Optional[str] = None):
        """진아브렐슈드 공략"""
        await self._handle_boss_command(ctx, '진아브렐슈드', difficulty)

    @boss.command(name='모르둠')
    async def mordum(self, ctx: commands.Context, difficulty: Optional[str] = None):
        """모르둠 공략"""
        await self._handle_boss_command(ctx, '모르둠', difficulty)

    async def _handle_boss_command(self, ctx: commands.Context, boss_name: str, difficulty: Optional[str] = None):
        """
        개별 보스 명령어 처리 함수
        :param ctx: discord.ext.commands.Context 객체 (명령어 컨텍스트)
        :param boss_name: str (보스 이름)
        :param difficulty: str (난이도, None일 수 있음)
        """
        if difficulty is None:
            await self._send_boss_selection(ctx, boss_name) # 난이도 선택 메시지 전송
            return

        if difficulty.lower() not in self.boss_data.get(boss_name,{}).get('difficulties', []): # 입력받은 난이도가 보스 데이터에 있는지 확인
            await ctx.send("올바른 난이도를 입력해주세요. (노말/하드)")
            return

        await self._show_difficulty_info(ctx, boss_name, difficulty) # 선택된 난이도 정보 표시

#====================================[봇 코드]=====================================
async def setup(bot):
    await bot.add_cog(ChatBot(bot)) #챗봇 명령어
    await bot.add_cog(Schedule(bot)) #일정 투표 명령어
    await bot.add_cog(BossStrategy(bot)) #보스 공략 명령어
    await bot.add_cog(PolicyCog(bot)) #정책사항 명령어


# 매주 수요일 오전 10시 05분에 공지사항 출력
schedule.add_job(send_LostArkNotice, CronTrigger(day_of_week="wed", hour=10, minute=5))

# 고유 토큰 및 bot 실행
bot.run(Token)