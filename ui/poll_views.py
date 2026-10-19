#====================================투표 UI 컴포넌트======================================
# 투표 관련 Discord UI 컴포넌트들을 관리합니다.

import discord
from discord import SelectOption
from discord.ui import Select, View
from utils.date_utils import (
    get_korean_weekday,
    format_korean_date,
    create_progress_bar,
    parse_date
)


class DateSelect(Select):
    """단일 선택 투표용 드롭다운 메뉴"""

    def __init__(self, dates):
        options = []
        for date in dates:
            date_obj = parse_date(date)
            weekday = get_korean_weekday(date_obj)
            options.append(
                SelectOption(
                    label=f"{date_obj.month}월 {date_obj.day}일 ({weekday})",
                    value=date,
                    description=f"{date_obj.year}년 {date_obj.month}월 {date_obj.day}일"
                )
            )

        super().__init__(
            placeholder="날짜를 선택하세요",
            min_values=1,
            max_values=1,
            options=options
        )
        self.votes = {}  # 투표 데이터

    async def callback(self, interaction):
        """투표 콜백 함수"""
        user_id = interaction.user.id
        selected_date = self.values[0]

        # 이전 투표와 동일한 경우 체크
        if user_id in self.votes:
            old_vote = self.votes[user_id]
            if old_vote == selected_date:
                await interaction.response.send_message("이미 선택한 날짜입니다!", ephemeral=True)
                return

        self.votes[user_id] = selected_date

        await interaction.response.send_message(f"'{selected_date}'에 투표하셨습니다!", ephemeral=True)

        # DM으로 투표 알림 전송
        try:
            date_obj = parse_date(selected_date)
            weekday = get_korean_weekday(date_obj)
            await interaction.user.send(
                f"📊 단일투표 알림\n"
                f"{interaction.message.embeds[0].title}에서\n"
                f"{date_obj.month}월 {date_obj.day}일 ({weekday})에 투표하셨습니다!"
            )
        except discord.Forbidden:
            pass

        # 투표 결과 업데이트
        await self._update_embed(interaction)

    async def _update_embed(self, interaction):
        """임베드 투표 결과 업데이트"""
        vote_counts = {}
        for date in self.votes.values():
            vote_counts[date] = vote_counts.get(date, 0) + 1

        embed = interaction.message.embeds[0]
        embed.clear_fields()

        total_votes = len(self.votes)
        max_votes = max(vote_counts.values()) if vote_counts else 0

        sorted_dates = sorted(vote_counts.items(), key=lambda x: x[1], reverse=True)

        for date, count in sorted_dates:
            date_obj = parse_date(date)
            weekday = get_korean_weekday(date_obj)
            percentage = (count / total_votes * 100) if total_votes > 0 else 0
            bar = create_progress_bar(count, max_votes)

            embed.add_field(
                name=f"{date_obj.month}월 {date_obj.day}일 ({weekday})",
                value=f"{bar} {count}명 ({percentage:.1f}%)",
                inline=False
            )

        await interaction.message.edit(embed=embed)


class PollView(View):
    """단일 선택 투표 뷰"""

    def __init__(self, dates):
        super().__init__(timeout=None)
        self.date_select = DateSelect(dates)
        self.add_item(self.date_select)


class MultiDateSelect(Select):
    """다중 선택 투표용 드롭다운 메뉴"""

    def __init__(self, dates):
        options = []
        for date in dates:
            date_obj = parse_date(date)
            weekday = get_korean_weekday(date_obj)
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
        self.votes = {}  # 투표 데이터

    async def callback(self, interaction):
        """투표 콜백 함수"""
        user_id = interaction.user.id
        selected_dates = self.values

        # 이전 투표와 동일한 경우 체크
        if user_id in self.votes and set(self.votes[user_id]) == set(selected_dates):
            await interaction.response.send_message("이미 동일한 날짜들을 선택하셨습니다!", ephemeral=True)
            return

        self.votes[user_id] = selected_dates

        await interaction.response.send_message(
            f"선택한 날짜: {', '.join(selected_dates)}에 투표하셨습니다!",
            ephemeral=True
        )

        # DM으로 투표 알림 전송
        try:
            dm_message = f"📊 중복투표 알림\n{interaction.message.embeds[0].title}에서\n선택하신 날짜:\n"
            for date in selected_dates:
                date_obj = parse_date(date)
                weekday = get_korean_weekday(date_obj)
                dm_message += f"• {date_obj.month}월 {date_obj.day}일 ({weekday})\n"

            await interaction.user.send(dm_message)
        except discord.Forbidden:
            pass

        # 투표 결과 업데이트
        await self._update_embed(interaction)

    async def _update_embed(self, interaction):
        """임베드 투표 결과 업데이트"""
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
            date_obj = parse_date(date)
            weekday = get_korean_weekday(date_obj)
            percentage = (count / total_votes * 100)
            bar = create_progress_bar(count, max_votes)

            embed.add_field(
                name=f"{date_obj.month}월 {date_obj.day}일 ({weekday})",
                value=f"{bar} {count}명 ({percentage:.1f}%)",
                inline=False
            )

        await interaction.message.edit(embed=embed)


class MultiPollView(View):
    """다중 선택 투표 뷰"""

    def __init__(self, dates):
        super().__init__(timeout=None)
        self.date_select = MultiDateSelect(dates)
        self.add_item(self.date_select)
