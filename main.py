#====================================라이브러리 설정======================================
from bs4 import BeautifulSoup
from data import Token, GEMINI_API_KEY, CHANNEL_ID #봇 토큰, Gemini API 키
from datetime import datetime #날짜 라이브러리
from discord.ext import commands #명령어 라이브러리
from discord import ButtonStyle, SelectOption #버튼 스타일, 드롭다운 메뉴 옵션 라이브러리
from discord.ui import Button, View, Select #버튼, 뷰, 드롭다운 메뉴 라이브러리
from apscheduler.schedulers.asyncio import AsyncIOScheduler #비동기 작업을 처리하기 위한 스케줄러
from apscheduler.triggers.cron import CronTrigger #스케줄을 설정할 때 CronTrigger 사용
import google.generativeai as genai #Gemini API 라이브러리
import discord #디스코드 라이브러리
import asyncio #비동기 라이브러리
import calendar #달력 라이브러리


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
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("무언가를"))

    schedule.start()
    for guild in bot.guilds:
        if guild.system_channel:
            await guild.system_channel.send(f'{bot.user.name}이 연결되었습니다!')
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
    
#===================================[봇 관련 명령어]====================================

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
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='보스', aliases=['boss', 'b'])
    async def boss(self, ctx):
        """보스 공략 명령어"""
        if ctx.invoked_subcommand is None:  # 하위 명령어가 없는 경우
            if len(ctx.message.content.split()) > 1:  # 잘못된 보스 이름이 입력된 경우
                embed = discord.Embed(
                    title="❌ 오류",
                    description="존재하지 않는 보스입니다.",
                    color=discord.Color.red()
                )
                
                embed.add_field(
                    name=Boss_List[0],  # 군단장 레이드
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
                    name=Boss_List[1],  # 에픽 레이드
                    value="• `/보스 베히모스` - 폭풍의 지휘관",
                    inline=False
                )

                embed.add_field(
                    name=Boss_List[2],  # 어비스 레이드
                    value=(
                        "• `/보스 카양겔` - 영원한 빛의 요람\n"
                        "• `/보스 상아탑` - 짓밟힌 정원"
                    ),
                    inline=False
                )

                embed.add_field(
                    name=Boss_List[3],  # 카제로스 레이드
                    value=(
                        "• `/보스 에키드나` - 서막\n"
                        "• `/보스 에기르` - 1막\n"
                        "• `/보스 진아브렐슈드` - 2막"
                        #"• `/보스 신규보스` - 3막"
                    ),
                    inline=False
                )
                
                embed.set_footer(text="💡 전체 보스 목록을 보려면 /보스를 입력하세요.")
                await ctx.send(embed=embed)
                return

            # 기본 보스 목록 표시 (기존 코드)
            embed = discord.Embed(
                title="🗡️ 로스트아크 레이드 공략",
                description="원하는 보스의 공략을 보려면 `/보스 [보스이름]`을 입력하세요.",
                color=discord.Color.blue()
            )

            # 군단장 레이드
            embed.add_field(name="🐺 발탄", value="`/보스 발탄` - 마수군단장", inline=True)
            embed.add_field(name="👻 비아키스", value="`/보스 비아키스` - 욕망군단장", inline=True)
            embed.add_field(name="🎭 쿠크세이튼", value="`/보스 쿠크세이튼` - 광기군단장", inline=True)
            embed.add_field(name="🌙 아브렐슈드", value="`/보스 아브렐슈드` - 몽환군단장", inline=True)
            embed.add_field(name="🦠 일리아칸", value="`/보스 일리아칸` - 질병군단장", inline=True)
            embed.add_field(name="⚡ 카멘", value="`/보스 카멘` - 어둠군단장", inline=True)

            # 에픽 레이드
            embed.add_field(name="🐉️ 베히모스", value="`/보스 베히모스` - 폭풍의 지휘관", inline=True)

            # 어비스 레이드
            embed.add_field(name="✨ 카양겔", value="`/보스 카양겔` - 영원한 빛의 요람", inline=True)            
            embed.add_field(name="🗼 상아탑", value="`/보스 상아탑` - 짓밟힌 정원", inline=True)
            
            # 카제로스 레이드
            embed.add_field(name="🐍 에키드나", value="`/보스 에키드나` - 서막 : 붉어진 백야의 나선", inline=True)
            embed.add_field(name="🔔 에기르", value="`/보스 에기르` - 1막 : 대지를 부수는 업화의 궤적", inline=True)
            embed.add_field(name="🥶 진아브렐슈드", value="`/보스 진아브렐슈드` - 2막 : 부유하는 악몽의 진혼곡", inline=True)
            #embed.add_field(name="🎷 신규보스이름", value="`/보스 신규보스` - 2막 : ", inline=True)
            embed.set_footer(text="💡 각 보스의 상세 공략을 보려면 해당 명령어를 입력하세요.")
            await ctx.send(embed=embed)

    @boss.command(name='발탄')
    async def valtan(self, ctx, difficulty=None):
        """발탄 공략"""
        if difficulty is None:
            embed = discord.Embed(
                title="🐺 발탄 공략 - 마수군단장",
                description="난이도를 선택해주세요: `/보스 발탄 [노말/하드]`",
                color=discord.Color.red()
            )
            embed.add_field(
                name="난이도 선택",
                value=(
                    "• `/보스 발탄 노말` - 노말 난이도 공략\n"
                    "• `/보스 발탄 하드` - 하드 난이도 공략"
                ),
                inline=False
            )
            await ctx.send(embed=embed)
            return

        if difficulty.lower() not in ['노말', '하드']:
            await ctx.send("올바른 난이도를 입력해주세요. (노말/하드)")
            return

        embed = discord.Embed(
            title=f"🐺 발탄 공략 ({difficulty}) - 마수군단장",
            description=f"난이도: {'⭐☆☆☆☆' if difficulty=='노말' else '⭐☆☆☆☆'}",
            color=discord.Color.red()
        )
        
        # 난이도별 이미지 경로 설정
        difficulty_path = 'normal' if difficulty=='노말' else 'hard'
        files = [
            discord.File(f"images/legion/valtan/{difficulty_path}/1gate.png", filename="valtan1.png"),
        ]
        
        embed.set_image(url="attachment://valtan1.png")
        await ctx.send(file=files[0], embed=embed)

    @boss.command(name='비아키스', aliases=['비아'])
    async def vykas(self, ctx, difficulty=None):
        """비아키스 공략"""
        if difficulty is None:
            embed = discord.Embed(
                title="👻 비아키스 공략 - 욕망군단장",
                description="난이도를 선택해주세요: `/보스 비아키스 [노말/하드]`",
                color=discord.Color.purple()
            )
            embed.add_field(
                name="난이도 선택",
                value=(
                    "• `/보스 비아키스 노말` - 노말 난이도 공략\n"
                    "• `/보스 비아키스 하드` - 하드 난이도 공략"
                ),
                inline=False
            )
            await ctx.send(embed=embed)
            return

        if difficulty.lower() not in ['노말', '하드']:
            await ctx.send("올바른 난이도를 입력해주세요. (노말/하드)")
            return

        embed = discord.Embed(
            title=f"👻 비아키스 공략 ({difficulty}) - 욕망군단장",
            description=f"난이도: {'⭐☆☆☆☆' if difficulty=='노말' else '⭐☆☆☆☆'}",
            color=discord.Color.purple()
        )
        
        difficulty_path = 'normal' if difficulty=='노말' else 'hard'
        files = [
            discord.File(f"images/legion/vykas/{difficulty_path}/1gate.png", filename="vykas1.png"),
        ]
        
        embed.set_image(url="attachment://vykas1.png")
        await ctx.send(file=files[0], embed=embed)

    @boss.command(name='쿠크세이튼', aliases=['쿠크'])
    async def kouku(self, ctx, difficulty='노말'):
        """쿠크세이튼 공략"""
        if difficulty not in ['노말']:
            embed = discord.Embed(
                title="🎭 쿠크세이튼 공략 - 광기군단장",
                description="난이도를 선택해주세요: `/보스 쿠크세이튼 [노말]",
                color=discord.Color.dark_gold()
            )
            embed.add_field(
                name="난이도 선택",
                value=(
                    "• `/보스 쿠크세이튼 노말` - 노말 난이도 공략"
                ),
                inline=False
            )
            await ctx.send(embed=embed)
            return

        if difficulty.lower() not in ['노말']:
            await ctx.send("올바른 난이도를 입력해주세요. (노말)")  
            return

        embed = discord.Embed(
            title=f"🎭 쿠크세이튼 공략 ({difficulty}) - 광기군단장",
            description=f"난이도: {'⭐☆☆☆☆' if difficulty=='노말' else '⭐☆☆☆☆'}",
            color=discord.Color.dark_gold()
        )
        
        difficulty_path = 'normal' if difficulty=='노말' else 'hard'
        files = [
            discord.File(f"images/legion/kouku/{difficulty_path}/1gate.png", filename="kouku1.png"),
            discord.File(f"images/legion/kouku/{difficulty_path}/2gate.png", filename="kouku2.png"),
            discord.File(f"images/legion/kouku/{difficulty_path}/3gate.png", filename="kouku3.png"),
        ]
        
        embed.set_image(url="attachment://kouku1.png")
        embeds = [embed]
        
        for i in range(1, len(files)):
            gate_embed = discord.Embed(
                title=f"{i+1}번 공략 ({difficulty})",
                color=discord.Color.dark_gold()
            )
            gate_embed.set_image(url=f"attachment://kouku{i+1}.png")
            embeds.append(gate_embed)
        
        await ctx.send(files=files, embeds=embeds)

    @boss.command(name='아브렐슈드', aliases=['아브'])
    async def abrelshud(self, ctx, difficulty=None):
        """아브렐슈드 공략"""
        if difficulty is None:
            embed = discord.Embed(
                title="🌙 아브렐슈드 공략 - 몽환군단장",
                description="난이도를 선택해주세요: `/보스 아브렐슈드 [노말/하드]`",
                color=discord.Color.dark_red()
            )
            embed.add_field(
                name="난이도 선택",
                value=(
                    "• `/보스 아브렐슈드 노말` - 노말 난이도 공략\n"
                    "• `/보스 아브렐슈드 하드` - 하드 난이도 공략"
                ),
                inline=False
            )
            await ctx.send(embed=embed)
            return

        if difficulty.lower() not in ['노말', '하드']:
            await ctx.send("올바른 난이도를 입력해주세요. (노말/하드)")
            return

        embed = discord.Embed(
            title=f"🌙 아브렐슈드 공략 ({difficulty}) - 몽환군단장",
            description=f"난이도: {'⭐☆☆☆☆' if difficulty=='노말' else '⭐☆☆☆☆'}",
            color=discord.Color.dark_red()
        )
        
        difficulty_path = 'normal' if difficulty=='노말' else 'hard'
        files = [
            discord.File(f"images/legion/abrelshud/{difficulty_path}/1gate.png", filename="abrel1.png"),
            discord.File(f"images/legion/abrelshud/{difficulty_path}/2gate.png", filename="abrel2.png"),
         ]
        
        embed.set_image(url="attachment://abrel1.png")
        embeds = [embed]
        
        for i in range(1, len(files)):
            gate_embed = discord.Embed(
                title=f"{i+1}번 공략 ({difficulty})",
                color=discord.Color.dark_red()
            )
            gate_embed.set_image(url=f"attachment://abrel{i+1}.png")
            embeds.append(gate_embed)
        
        await ctx.send(files=files, embeds=embeds)

    @boss.command(name='일리아칸', aliases=['일리', '아칸'])
    async def illakan(self, ctx, difficulty=None):
        """일리아칸 공략"""
        if difficulty is None:
            embed = discord.Embed(
                title="🦠 일리아칸 공략 - 질병군단장",
                description="난이도를 선택해주세요: `/보스 일리아칸 [노말/하드]`",
                color=discord.Color.gold()
            )
            embed.add_field(
                name="난이도 선택",
                value=(
                    "• `/보스 일리아칸 노말` - 노말 난이도 공략\n"
                    "• `/보스 일리아칸 하드` - 하드 난이도 공략"
                ),
                inline=False
            )
            await ctx.send(embed=embed)
            return

        if difficulty.lower() not in ['노말', '하드']:
            await ctx.send("올바른 난이도를 입력해주세요. (노말/하드)")
            return

        embed = discord.Embed(
            title=f"🦠 일리아칸 공략 ({difficulty}) - 질병군단장",
            description=f"난이도: {'⭐☆☆☆☆' if difficulty=='노말' else '⭐☆☆☆☆'}",
            color=discord.Color.gold()
        )
        
        difficulty_path = 'normal' if difficulty=='노말' else 'hard'
        files = [
            discord.File(f"images/legion/illakan/{difficulty_path}/1gate.png", filename="illakan1.png"),
            discord.File(f"images/legion/illakan/{difficulty_path}/2gate.png", filename="illakan2.png"),
            discord.File(f"images/legion/illakan/{difficulty_path}/3gate.png", filename="illakan3.png"),
        ]
        
        embed.set_image(url="attachment://illakan1.png")
        embeds = [embed]
        
        for i in range(1, len(files)):
            gate_embed = discord.Embed(
                title=f"{i+1}번 공략 ({difficulty})",
                color=discord.Color.gold()
            )
            gate_embed.set_image(url=f"attachment://illakan{i+1}.png")
            embeds.append(gate_embed)
        
        await ctx.send(files=files, embeds=embeds)

    @boss.command(name='카멘')
    async def kamen(self, ctx, difficulty=None):
        """카멘 공략"""
        if difficulty is None:
            embed = discord.Embed(
                title="⚡ 카멘 공략 - 어둠군단장",
                description="난이도를 선택해주세요: `/보스 카멘 [노말/하드]`",
                color=discord.Color.dark_purple()
            )
            embed.add_field(
                name="난이도 선택",
                value=(
                    "• `/보스 카멘 노말` - 노말 난이도 공략 (1-3관문)\n"
                    "• `/보스 카멘 하드` - 하드 난이도 공략 (1-4관문)"
                ),
                inline=False
            )
            await ctx.send(embed=embed)
            return

        if difficulty.lower() not in ['노말', '하드']:
            await ctx.send("올바른 난이도를 입력해주세요. (노말/하드)")
            return

        embed = discord.Embed(
            title=f"⚡ 카멘 공략 ({difficulty}) - 어둠군단장",
            description=f"난이도: {'⭐⭐⭐☆☆' if difficulty=='노말' else '⭐⭐⭐⭐☆'}",
            color=discord.Color.dark_purple()
        )
        
        difficulty_path = 'normal' if difficulty=='노말' else 'hard'
        # 난이도별로 다른 관문 수 설정
        files = [
            discord.File(f"images/legion/kamen/{difficulty_path}/1gate.png", filename="kamen1.png"),
            discord.File(f"images/legion/kamen/{difficulty_path}/2gate.png", filename="kamen2.png"),
        ]
        
        # 하드 난이도일 경우 3,4관문 추가
        if difficulty == '하드':
            files.extend([
                discord.File(f"images/legion/kamen/{difficulty_path}/3gate.png", filename="kamen3.png"),
                discord.File(f"images/legion/kamen/{difficulty_path}/4gate.png", filename="kamen4.png"),
            ])
        
        embed.set_image(url="attachment://kamen1.png")
        embeds = [embed]
        
        for i in range(1, len(files)):
            gate_embed = discord.Embed(
                title=f"{i+1}번 공략 ({difficulty})",
                color=discord.Color.dark_purple() 
            )
            gate_embed.set_image(url=f"attachment://kamen{i+1}.png")
            embeds.append(gate_embed)
        
        await ctx.send(files=files, embeds=embeds)

    @boss.command(name='베히모스', aliases=['베히'])
    async def behimos(self, ctx, difficulty='노말'):
        """베히모스 공략"""
        if difficulty not in ['노말']:
            embed = discord.Embed(
                title="🐉️ 베히모스 공략 - 폭풍의 지휘관",
                description="난이도를 선택해주세요: `/보스 베히모스 노말",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="난이도 선택",
                value="• `/보스 베히모스 노말` - 노말 난이도 공략",  # 노말만 표시
                inline=False
            )
            await ctx.send(embed=embed)
            return

        if difficulty.lower() != '노말':  # 노말만 허용
            await ctx.send("베히모스는 노말 난이도만 존재합니다.")
            return

        embed = discord.Embed(
            title=f"🐉️ 베히모스 공략 ({difficulty}) - 폭풍의 지휘관",
            description="난이도: ⭐☆☆☆☆",  # 노말 난이도로 고정
            color=discord.Color.blue()
        )
        
        files = [
            discord.File("images/epic/behimos/normal/1gate.png", filename="behimos1.png"),
        ]
        
        embed.set_image(url="attachment://behimos1.png")
        await ctx.send(file=files[0], embed=embed)

    @boss.command(name='카양겔', aliases=['양겔'])
    async def kayangel(self, ctx, difficulty=None):
        """카양겔 공략"""
        if difficulty is None:
            embed = discord.Embed(
                title="✨ 카양겔 공략 - 영원한 빛의 요람",
                description="난이도를 선택해주세요: `/보스 카양겔 [노말/하드]`",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="난이도 선택",
                value=(
                    "• `/보스 카양겔 노말` - 노말 난이도 공략\n"
                    "• `/보스 카양겔 하드` - 하드 난이도 공략"
                ),
                inline=False
            )
            await ctx.send(embed=embed)
            return

        if difficulty.lower() not in ['노말', '하드']:
            await ctx.send("올바른 난이도를 입력해주세요. (노말/하드)")
            return

        embed = discord.Embed(
            title=f"✨ 카양겔 공략 ({difficulty}) - 영원한 빛의 요람",
            description=f"난이도: {'⭐☆☆☆☆' if difficulty=='노말' else '⭐☆☆☆☆'}",
            color=discord.Color.blue()
        )
        
        difficulty_path = 'normal' if difficulty=='노말' else 'hard'
        files = [
            discord.File(f"images/abyss/kayangel/{difficulty_path}/1gate.png", filename="kayangel1.png"),
        ]
        
        embed.set_image(url="attachment://kayangel1.png")
        await ctx.send(file=files[0], embed=embed)

    @boss.command(name='상아탑', aliases=['탑'])
    async def tower(self, ctx, difficulty=None):
        """상아탑 공략"""
        if difficulty is None:
            embed = discord.Embed(
                title="🗼 상아탑 공략 - 짓밟힌 정원",
                description="난이도를 선택해주세요: `/보스 상아탑 [노말/하드]`",
                color=discord.Color.light_grey()
            )
            embed.add_field(
                name="난이도 선택",
                value=(
                    "• `/보스 상아탑 노말` - 노말 난이도 공략\n"
                    "• `/보스 상아탑 하드` - 하드 난이도 공략"
                ),
                inline=False
            )
            await ctx.send(embed=embed)
            return

        if difficulty.lower() not in ['노말', '하드']:
            await ctx.send("올바른 난이도를 입력해주세요. (노말/하드)")
            return

        embed = discord.Embed(
            title=f"🗼 상아탑 공략 ({difficulty}) - 짓밟힌 정원",
            description=f"난이도: {'⭐☆☆☆☆' if difficulty=='노말' else '⭐☆☆☆☆'}",
            color=discord.Color.light_grey()
        )
        
        difficulty_path = 'normal' if difficulty=='노말' else 'hard'
        files = [
            discord.File(f"images/abyss/tower/{difficulty_path}/1gate.png", filename="tower1.png"),
            discord.File(f"images/abyss/tower/{difficulty_path}/2gate.png", filename="tower2.png"),
            discord.File(f"images/abyss/tower/{difficulty_path}/3gate.png", filename="tower3.png"),
        ]
        
        embed.set_image(url="attachment://tower1.png")
        embeds = [embed]
        
        for i in range(1, len(files)):
            gate_embed = discord.Embed(
                title=f"{i+1}번 공략 ({difficulty})",
                color=discord.Color.light_grey()
            )
            gate_embed.set_image(url=f"attachment://tower{i+1}.png")
            embeds.append(gate_embed)
        
        await ctx.send(files=files, embeds=embeds)

    @boss.command(name='에키드나', aliases=['에키'])
    async def ekidna(self, ctx, difficulty=None):
        """에키드나 공략"""
        if difficulty is None:
            embed = discord.Embed(
                title="🐍 에키드나 공략 - 서막 : 붉어진 백야의 나선",
                description="난이도를 선택해주세요: `/보스 에키드나 [노말/하드]`",
                color=discord.Color.green()
            )
            embed.add_field(
                name="난이도 선택",
                value=(
                    "• `/보스 에키드나 노말` - 노말 난이도 공략\n"
                    "• `/보스 에키드나 하드` - 하드 난이도 공략"
                ),
                inline=False
            )
            await ctx.send(embed=embed)
            return

        if difficulty.lower() not in ['노말', '하드']:
            await ctx.send("올바른 난이도를 입력해주세요. (노말/하드)")
            return

        embed = discord.Embed(
            title=f"🐍 에키드나 공략 ({difficulty}) - 서막 : 붉어진 백야의 나선",
            description=f"난이도: {'⭐⭐☆☆☆' if difficulty=='노말' else '⭐⭐☆☆☆'}",
            color=discord.Color.green()
        )
        
        difficulty_path = 'normal' if difficulty=='노말' else 'hard'
        files = [
            discord.File(f"images/kazeros/ekidna/{difficulty_path}/1gate.png", filename="ekidna1.png"),
            discord.File(f"images/kazeros/ekidna/{difficulty_path}/2gate.png", filename="ekidna2.png"),
        ]
        
        embed.set_image(url="attachment://ekidna1.png")
        embeds = [embed]
        
        for i in range(1, len(files)):
            gate_embed = discord.Embed(
                title=f"{i+1}번 공략 ({difficulty})",
                color=discord.Color.green()
            )
            gate_embed.set_image(url=f"attachment://ekidna{i+1}.png")
            embeds.append(gate_embed)
        
        await ctx.send(files=files, embeds=embeds)

    @boss.command(name='에기르', aliases=['에기', '기르'])
    async def aegir1(self, ctx, difficulty=None):
        """에기르 1막 공략"""
        if difficulty is None:
            embed = discord.Embed(
                title="🔔 에기르 공략 - 1막 : 대지를 부수는 업화의 궤적",
                description="난이도를 선택해주세요: `/보스 에기르 [노말/하드]`",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="난이도 선택",
                value=(
                    "• `/보스 에기르 노말` - 노말 난이도 공략\n"
                    "• `/보스 에기르 하드` - 하드 난이도 공략"
                ),
                inline=False
            )
            await ctx.send(embed=embed)
            return

        if difficulty.lower() not in ['노말', '하드']:
            await ctx.send("올바른 난이도를 입력해주세요. (노말/하드)")
            return

        embed = discord.Embed(
            title=f"🔔 에기르 공략 ({difficulty}) - 1막 : 대지를 부수는 업화의 궤적",
            description=f"난이도: {'⭐☆☆☆☆' if difficulty=='노말' else '⭐☆☆☆☆'}",
            color=discord.Color.blue()
        )
        
        difficulty_path = 'normal' if difficulty=='노말' else 'hard'
        files = [
            discord.File(f"images/kazeros/aegir/{difficulty_path}/1gate.png", filename="aegir1.png"),
            discord.File(f"images/kazeros/aegir/{difficulty_path}/2gate.png", filename="aegir2.png"),
        ]
        
        embed.set_image(url="attachment://aegir1.png")
        embeds = [embed]
        
        for i in range(1, len(files)):
            gate_embed = discord.Embed(
                title=f"{i+1}번 공략 ({difficulty})",
                color=discord.Color.blue()
            )
            gate_embed.set_image(url=f"attachment://aegir{i+1}.png")
            embeds.append(gate_embed)
        
        await ctx.send(files=files, embeds=embeds)

    @boss.command(name='진아브렐슈드', aliases=['진아브'])
    async def aegir2(self, ctx, difficulty=None):
        """진아브렐슈드 공략"""
        if difficulty is None:
            embed = discord.Embed(
                title="🥶 진아브렐슈드 공략 - 2막 : 부유하는 악몽의 진혼곡",
                description="난이도를 선택해주세요: `/보스 진아브렐슈드 [노말/하드]`",
                color=discord.Color.dark_blue()
            )
            embed.add_field(
                name="난이도 선택",
                value=(
                    "• `/보스 진아브렐슈드 노말` - 노말 난이도 공략 (1-2관문)\n"
                    "• `/보스 진아브렐슈드 하드` - 하드 난이도 공략 (1-2관문)"
                ),
                inline=False
            )
            await ctx.send(embed=embed)
            return
            
        if difficulty.lower() not in ['노말', '하드']:
            await ctx.send("올바른 난이도를 입력해주세요. (노말/하드)")
            return

        embed = discord.Embed(
            title=f"🥶 진아브렐슈드 공략 ({difficulty}) - 2막 : 부유하는 악몽의 진혼곡",
            description=f"난이도: {'⭐⭐⭐☆☆' if difficulty=='노말' else '⭐⭐⭐☆☆'}",
            color=discord.Color.dark_blue()
        )
        
        difficulty_path = 'normal' if difficulty=='노말' else 'hard'
        # 난이도별로 다른 관문 수 설정
        files = [
            discord.File(f"images/kazeros/abrel/{difficulty_path}/1gate.png", filename="abrel1.png"),
            discord.File(f"images/kazeros/abrel/{difficulty_path}/2gate.png", filename="abrel2.png"),
        ]
        
        # 노말 난이도일 경우 3관문 추가
        if difficulty == '노말':
            files.append(
                discord.File(f"images/kazeros/abrel/{difficulty_path}/3gate.png", filename="abrel3.png"),
            )
        
        embed.set_image(url="attachment://abrel1.png")
        embeds = [embed]
        
        for i in range(1, len(files)):
            gate_embed = discord.Embed(
                title=f"{i+1}번 공략 ({difficulty})",
                color=discord.Color.dark_blue()
            )
            gate_embed.set_image(url=f"attachment://abrel{i+1}.png")
            embeds.append(gate_embed)
        
        await ctx.send(files=files, embeds=embeds)
"""
    @boss.command(name='신규보스', aliases=['신규보스'])
    async def verber(self, ctx, difficulty=None):
        #신규보스
        if difficulty is None:
            embed = discord.Embed(
                title="🎷 신규보스 - 3막 : ",
                description="난이도를 선택해주세요: `/보스 신규보스 [노말/하드]`",
                color=discord.Color.dark_yellow()
            )
            embed.add_field(
                name="난이도 선택",
                value=(
                    "• `/보스 신규보스 노말` - 노말 난이도 공략 (1-2관문)\n"
                    "• `/보스 신규보스 하드` - 하드 난이도 공략 (1-2관문)"
                ),
                inline=False
            )
            await ctx.send(embed=embed)
            return
            
        if difficulty.lower() not in ['노말', '하드']:
            await ctx.send("올바른 난이도를 입력해주세요. (노말/하드)")
            return

        embed = discord.Embed(
            title=f"🎷 신규보스 공략 ({difficulty}) - 3막 : ",
            description=f"난이도: {'⭐⭐⭐☆☆' if difficulty=='노말' else '⭐⭐⭐☆☆'}",
            color=discord.Color.dark_yellow()
        )
        
        difficulty_path = 'normal' if difficulty=='노말' else 'hard'
        # 난이도별로 다른 관문 수 설정
        files = [
            discord.File(f"images/kazeros/신규보스/{difficulty_path}/1gate.png", filename="신규보스1.png"),
            discord.File(f"images/kazeros/신규보스/{difficulty_path}/2gate.png", filename="신규보스2.png"),
        ]
        
        # 노말 난이도일 경우 3관문 추가
        if difficulty == '노말':
            files.append(
                discord.File(f"images/kazeros/신규보스/{difficulty_path}/3gate.png", filename="신규보스3.png"),
            )
        
        embed.set_image(url="attachment://신규보스1.png")
        embeds = [embed]
        
        for i in range(1, len(files)):
            gate_embed = discord.Embed(
                title=f"{i+1}번 공략 ({difficulty})",
                color=discord.Color.dark_yellow()
            )
            gate_embed.set_image(url=f"attachment://신규보스{i+1}.png")
            embeds.append(gate_embed)
        
        await ctx.send(files=files, embeds=embeds)
"""


#====================================[봇 코드]=====================================
async def setup(bot):
    await bot.add_cog(ChatBot(bot)) #챗봇 명령어
    await bot.add_cog(Schedule(bot)) #일정 투표 명령어
    await bot.add_cog(BossStrategy(bot)) #보스 공략 명령어

# 매주 수요일 오전 10시 05분에 공지사항 출력
schedule.add_job(send_LostArkNotice, CronTrigger(day_of_week="wed", hour=10, minute=5))

# 고유 토큰 및 bot 실행
bot.run(Token)