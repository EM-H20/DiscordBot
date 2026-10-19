#====================================일정 투표 Cog======================================
# 투표 관련 명령어들을 관리합니다. (단일투표, 중복투표, 투표목록, 투표종료)

import discord
from discord.ext import commands
import asyncio
from datetime import datetime

from config import MAX_POLL_DATES, POLL_TIMEOUT
from ui.poll_views import PollView, MultiPollView, MultiDateSelect
from utils.date_utils import get_korean_weekday, create_progress_bar, parse_date


class ScheduleCog(commands.Cog):
    """일정 투표 명령어 Cog"""

    def __init__(self, bot):
        self.bot = bot
        self.active_polls = {}  # 진행 중인 투표 데이터

    @commands.command(name='단일투표')
    async def create_poll(self, ctx, title=None, *dates):
        """
        단일 선택 투표를 생성합니다.
        :param title: 투표 제목
        :param dates: 날짜 목록 (YYYY-MM-DD 형식)
        """
        # 유효성 검사
        error_msg = self._validate_poll_input(title, dates)
        if error_msg:
            await ctx.send(error_msg)
            return

        embed = discord.Embed(
            title=f"📅 {title}",
            description="아래 드롭다운 메뉴에서 선호하는 날짜를 선택해주세요.",
            color=discord.Color.blue()
        )

        view = PollView(dates)
        message = await ctx.send(embed=embed, view=view)
        self.active_polls[message.id] = view.date_select

    @commands.command(name='중복투표')
    async def create_multi_poll(self, ctx, title=None, *dates):
        """
        다중 선택 투표를 생성합니다.
        :param title: 투표 제목
        :param dates: 날짜 목록 (YYYY-MM-DD 형식)
        """
        # 유효성 검사
        error_msg = self._validate_poll_input(title, dates)
        if error_msg:
            await ctx.send(error_msg)
            return

        embed = discord.Embed(
            title=f"📅 {title}",
            description="아래 드롭다운 메뉴에서 가능한 날짜를 모두 선택해주세요.",
            color=discord.Color.blue()
        )

        view = MultiPollView(dates)
        message = await ctx.send(embed=embed, view=view)
        self.active_polls[message.id] = view.date_select

    def _validate_poll_input(self, title, dates):
        """
        투표 입력 유효성 검사
        :return: 오류 메시지 또는 None
        """
        if title is None:
            return "투표 제목을 입력해주세요!"

        if len(dates) == 0:
            return "날짜를 최소 1개 이상 입력해주세요!"

        if len(dates) > MAX_POLL_DATES:
            return f"최대 {MAX_POLL_DATES}개까지의 날짜만 선택 가능합니다!"

        try:
            for date in dates:
                datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return "날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식으로 입력해주세요."

        return None

    @commands.command(name='투표종료')
    async def end_poll(self, ctx, *, title=None):
        """
        진행 중인 투표를 종료합니다.
        :param title: 종료할 투표 제목
        """
        try:
            if title is None:
                await ctx.send("투표 제목을 입력해주세요! 투표 목록을 보려면 `/투표목록`을 입력하세요.")
                return

            found_polls = []
            async for message in ctx.channel.history(limit=100):
                if message.embeds and message.id in self.active_polls:
                    message_title = message.embeds[0].title.replace("📅 ", "").strip()
                    if message_title == title:
                        date_select = self.active_polls.get(message.id)
                        if not date_select:
                            continue
                        poll_type = "중복" if isinstance(date_select, MultiDateSelect) else "단일"
                        found_polls.append((message, poll_type))

            if not found_polls:
                await ctx.send(f"'{title}' 제목의 진행 중인 투표를 찾을 수 없습니다.")
                return

            # 여러 개의 동일 제목 투표가 있는 경우
            if len(found_polls) > 1:
                message, poll_type = await self._select_poll_from_list(ctx, title, found_polls)
                if message is None:
                    return
            else:
                message, poll_type = found_polls[0]

            date_select = self.active_polls.get(message.id)
            if not date_select:
                await ctx.send("투표 데이터를 찾을 수 없습니다.")
                return

            if not date_select.votes:
                await ctx.send("아직 투표가 없습니다.")
                return

            # 투표 결과 계산 및 표시
            result_embed = self._create_result_embed(title, poll_type, date_select)
            await ctx.send(embed=result_embed)

            # 원본 투표 메시지 수정
            new_embed = message.embeds[0]
            new_embed.description = "🔒 투표가 종료되었습니다."
            await message.edit(embed=new_embed, view=None)

            del self.active_polls[message.id]

        except discord.NotFound:
            await ctx.send("메시지를 찾을 수 없습니다.")
        except discord.Forbidden:
            await ctx.send("메시지를 수정할 권한이 없습니다.")
        except Exception as e:
            await ctx.send(f"오류가 발생했습니다: {e}")
            print(f"Error in end_poll: {e}")

    async def _select_poll_from_list(self, ctx, title, found_polls):
        """여러 투표 중 하나를 선택하게 합니다."""
        select_embed = discord.Embed(
            title=f"📊 '{title}' 투표 선택",
            description="종료하려는 투표의 번호를 입력해주세요. (예: 1)",
            color=discord.Color.blue()
        )

        for i, (msg, poll_type) in enumerate(found_polls, 1):
            vote_count = len(self.active_polls[msg.id].votes)
            select_embed.add_field(
                name=f"{i}. {title} ({poll_type}투표)",
                value=f"현재 {vote_count}명 참여 중",
                inline=False
            )

        await ctx.send(embed=select_embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit()

        try:
            msg = await self.bot.wait_for('message', check=check, timeout=POLL_TIMEOUT)
            selection = int(msg.content)
            if 1 <= selection <= len(found_polls):
                return found_polls[selection - 1]
            else:
                await ctx.send("올바른 번호를 입력해주세요.")
                return None, None
        except asyncio.TimeoutError:
            await ctx.send("시간이 초과되었습니다. 다시 시도해주세요.")
            return None, None

    def _create_result_embed(self, title, poll_type, date_select):
        """투표 결과 임베드를 생성합니다."""
        vote_counts = {}

        if isinstance(date_select, MultiDateSelect):
            for user_votes in date_select.votes.values():
                for date in user_votes:
                    vote_counts[date] = vote_counts.get(date, 0) + 1
            total_votes = sum(vote_counts.values())
        else:
            for date in date_select.votes.values():
                vote_counts[date] = vote_counts.get(date, 0) + 1
            total_votes = len(date_select.votes)

        result_embed = discord.Embed(
            title=f"📊 투표 결과: {title}",
            description=f"총 투표 수: {total_votes}명 ({poll_type}투표)",
            color=discord.Color.green()
        )

        sorted_results = sorted(vote_counts.items(), key=lambda x: x[1], reverse=True)
        if sorted_results:
            max_votes = sorted_results[0][1]

            for date, count in sorted_results:
                date_obj = parse_date(date)
                weekday = get_korean_weekday(date_obj)
                percentage = (count / total_votes * 100)
                bar = create_progress_bar(count, max_votes)

                result_embed.add_field(
                    name=f"{date_obj.month}월 {date_obj.day}일 ({weekday})",
                    value=f"{bar} {count}명 ({percentage:.1f}%)",
                    inline=False
                )

            # 최다 선택된 날짜 표시
            winners = [date for date, votes in sorted_results if votes == max_votes]
            winner_text = self._format_winners(winners)
            result_embed.set_footer(text=winner_text)

        # 날짜별 투표자 표시
        date_voters = self._get_date_voters(date_select)
        if date_voters:
            voter_text = self._format_date_voters(date_voters)
            result_embed.add_field(
                name="📢 날짜별 투표 참여자",
                value=voter_text,
                inline=False
            )

        return result_embed

    def _format_winners(self, winners):
        """최다 선택된 날짜를 포맷합니다."""
        if len(winners) == 1:
            date_obj = parse_date(winners[0])
            weekday = get_korean_weekday(date_obj)
            return f"✨ 최다 선택된 날짜: {date_obj.month}월 {date_obj.day}일 ({weekday})"
        else:
            winner_texts = []
            for date in winners:
                date_obj = parse_date(date)
                weekday = get_korean_weekday(date_obj)
                winner_texts.append(f"{date_obj.month}월 {date_obj.day}일 ({weekday})")
            return f"✨ 최다 선택된 날짜들: {', '.join(winner_texts)}"

    def _get_date_voters(self, date_select):
        """날짜별 투표자 목록을 반환합니다."""
        date_voters = {}
        if isinstance(date_select, MultiDateSelect):
            for user_id, dates in date_select.votes.items():
                for date in dates:
                    if date not in date_voters:
                        date_voters[date] = []
                    date_voters[date].append(user_id)
        else:
            for user_id, date in date_select.votes.items():
                if date not in date_voters:
                    date_voters[date] = []
                date_voters[date].append(user_id)
        return date_voters

    def _format_date_voters(self, date_voters):
        """날짜별 투표자를 포맷합니다."""
        lines = []
        for date in sorted(date_voters.keys()):
            date_obj = parse_date(date)
            weekday = get_korean_weekday(date_obj)
            voters = " ".join(f"<@{user_id}>" for user_id in date_voters[date])
            lines.append(f"{date_obj.month}월 {date_obj.day}일 ({weekday}): {voters}")
        return "\n".join(lines)

    @commands.command(name='투표목록')
    async def list_polls(self, ctx):
        """현재 진행 중인 모든 투표 목록을 표시합니다."""
        if not self.active_polls:
            await ctx.send("진행 중인 투표가 없습니다.")
            return

        try:
            messages = {msg.id: msg async for msg in ctx.channel.history(limit=100)}

            # 삭제된 메시지의 투표 데이터 정리
            to_remove = [msg_id for msg_id in self.active_polls if msg_id not in messages]
            for msg_id in to_remove:
                del self.active_polls[msg_id]

            if not self.active_polls:
                await ctx.send("진행 중인 투표가 없습니다.")
                return

            embed = discord.Embed(
                title="📋 진행 중 투표 목록",
                description="투표를 종료하려면 `/투표종료 [제목]`을 입력하세요.",
                color=discord.Color.blue()
            )

            for msg_id, date_select in self.active_polls.items():
                if msg_id in messages:
                    message = messages[msg_id]
                    if message.embeds:
                        title = message.embeds[0].title.replace("📅 ", "")
                        vote_count = len(date_select.votes)
                        poll_type = "중복" if isinstance(date_select, MultiDateSelect) else "단일"
                        embed.add_field(
                            name=f"📊 {title}",
                            value=f"현재 {vote_count}명 참여 중 ({poll_type}투표)",
                            inline=False
                        )

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"투표 목록을 가져오는 중 오류가 발생했습니다: {e}")


async def setup(bot):
    """Cog 등록"""
    await bot.add_cog(ScheduleCog(bot))
