#====================================보스 공략 Cog======================================
# 보스 공략 관련 명령어들을 관리합니다.

import discord
from discord.ext import commands
import asyncio
import json
from typing import Dict, List, Optional, Any

from config import RAID_CATEGORIES, BOSS_SELECTION_TIMEOUT, DIFFICULTY_EMOJIS


class BossStrategyCog(commands.Cog):
    """보스 공략 명령어 Cog"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.boss_data: Dict[str, Any] = self._load_boss_data()

    def _load_boss_data(self) -> Dict[str, Any]:
        """JSON 파일에서 보스 데이터를 로드합니다."""
        with open('boss_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data['bosses']

    async def _send_embed(self, ctx: commands.Context, embed: discord.Embed, files: Optional[List[discord.File]] = None):
        """임베드와 파일을 전송합니다."""
        if files:
            await ctx.send(embed=embed)
            await asyncio.sleep(0.1)
            await ctx.send(file=files[0])
        else:
            await ctx.send(embed=embed)

    async def _send_boss_selection(self, ctx: commands.Context, boss_name: str):
        """보스 선택 임베드 메시지를 보내고 난이도 선택을 처리합니다."""
        boss_info = self.boss_data.get(boss_name)
        if not boss_info:
            await ctx.send("해당 보스 정보가 없습니다.")
            return

        embed = discord.Embed(
            title=f"⚔️ {boss_name} 공략 정보 선택",
            description="난이도를 선택하세요.",
            color=discord.Color.gold()
        )

        emojis = [DIFFICULTY_EMOJIS.get(d, '❓') for d in boss_info['difficulties']]
        emoji_str = ' '.join([f"{e} : {'노말' if e == '🇳' else '하드'}" for e in emojis])
        embed.add_field(name="난이도 선택", value=emoji_str, inline=False)

        msg = await ctx.send(embed=embed)
        for emoji in emojis:
            await msg.add_reaction(emoji)

        def check(reaction: discord.Reaction, user: discord.User) -> bool:
            return (
                user == ctx.author and
                str(reaction.emoji) in emojis and
                reaction.message.id == msg.id
            )

        try:
            reaction, user = await self.bot.wait_for(
                'reaction_add',
                timeout=BOSS_SELECTION_TIMEOUT,
                check=check
            )
            selected_difficulty = '노말' if str(reaction.emoji) == '🇳' else '하드'
            await self._show_difficulty_info(ctx, boss_name, selected_difficulty)
        except asyncio.TimeoutError:
            pass
        finally:
            await msg.delete()

    async def _show_difficulty_info(self, ctx: commands.Context, boss_name: str, difficulty: str):
        """선택된 난이도에 맞는 보스 공략 정보를 표시합니다."""
        boss_info = self.boss_data.get(boss_name)
        if not boss_info:
            await ctx.send("해당 보스 정보가 없습니다.")
            return

        difficulty_path = 'normal' if difficulty == '노말' else 'hard'

        if boss_info['gate_count'].get(difficulty, 0) > 0:
            for i in range(1, boss_info['gate_count'][difficulty] + 1):
                file_path = f"{boss_info['image_path']}/{difficulty_path}/{i}gate.png"
                try:
                    file = discord.File(file_path, filename=f"{boss_name.lower()}{i}.png")

                    embed = discord.Embed(
                        title=f"⚔️ {boss_info['name']} 공략 ({difficulty}) - {boss_info['description']}",
                        description=f"{i}번 공략\n난이도: {boss_info['difficulty_stars'][difficulty]}",
                        color=getattr(discord.Color, boss_info['color'])()
                    )
                    await self._send_embed(ctx, embed, [file])
                except FileNotFoundError:
                    await ctx.send(f"오류: `{file_path}` 파일이 없습니다.")
                    return
        else:
            await ctx.send("해당 난이도에 대한 정보가 없습니다.")

    def _group_bosses(self) -> Dict[str, List[str]]:
        """보스 정보를 종류별로 묶어 반환합니다."""
        bosses = {category: [] for category in RAID_CATEGORIES}

        for boss_name, boss_info in self.boss_data.items():
            description = boss_info['description']
            if '군단장' in description:
                bosses['군단장 레이드'].append(boss_name)
            elif '지휘관' in description:
                bosses['에픽 레이드'].append(boss_name)
            elif '요람' in description or '정원' in description:
                bosses['어비스 레이드'].append(boss_name)
            elif '막' in description or '서막' in description:
                bosses['카제로스 레이드'].append(boss_name)

        return bosses

    @commands.group(name='보스', aliases=['boss', 'b'])
    async def boss(self, ctx: commands.Context):
        """보스 공략 명령어 그룹"""
        if ctx.invoked_subcommand is None:
            if len(ctx.message.content.split()) > 1:
                # 존재하지 않는 보스 입력 시
                embed = discord.Embed(
                    title="❌ 오류",
                    description="존재하지 않는 보스입니다.",
                    color=discord.Color.red()
                )

                for category, bosses in self._group_bosses().items():
                    if bosses:
                        boss_list = "\n• ".join([
                            f"`/보스 {boss}` - {self.boss_data[boss]['description']}"
                            for boss in bosses
                        ])
                        embed.add_field(name=category, value=f"• {boss_list}", inline=False)

                embed.set_footer(text="💡 전체 보스 목록을 보려면 /보스를 입력하세요.")
                await self._send_embed(ctx, embed)
                return

            # 기본 보스 목록 표시
            embed = discord.Embed(
                title="🗡️ 로스트아크 레이드 공략",
                description="원하는 보스의 공략을 보려면 `/보스 [보스이름]`을 입력하세요.",
                color=discord.Color.blue()
            )

            for category, bosses in self._group_bosses().items():
                for boss in bosses:
                    embed.add_field(
                        name=f"{boss} ({self.boss_data[boss]['name']})",
                        value=f"`/보스 {boss}` - {self.boss_data[boss]['description']}",
                        inline=True
                    )

            embed.set_footer(text="💡 각 보스의 상세 공략을 보려면 해당 명령어를 입력하세요.")
            await self._send_embed(ctx, embed)

    async def _handle_boss_command(self, ctx: commands.Context, boss_name: str, difficulty: Optional[str] = None):
        """개별 보스 명령어를 처리합니다."""
        if difficulty is None:
            await self._send_boss_selection(ctx, boss_name)
            return

        valid_difficulties = self.boss_data.get(boss_name, {}).get('difficulties', [])
        if difficulty.lower() not in [d.lower() for d in valid_difficulties]:
            await ctx.send("올바른 난이도를 입력해주세요. (노말/하드)")
            return

        await self._show_difficulty_info(ctx, boss_name, difficulty)

    # ==================== 군단장 레이드 ====================
    @boss.command(name='발탄')
    async def valtan(self, ctx: commands.Context, difficulty: Optional[str] = None):
        """발탄 공략"""
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

    # ==================== 에픽 레이드 ====================
    @boss.command(name='베히모스', aliases=['베히'])
    async def behimos(self, ctx: commands.Context, difficulty: Optional[str] = None):
        """베히모스 공략"""
        await self._handle_boss_command(ctx, '베히모스', difficulty)

    # ==================== 어비스 레이드 ====================
    @boss.command(name='카양겔', aliases=['양겔'])
    async def kayangel(self, ctx: commands.Context, difficulty: Optional[str] = None):
        """카양겔 공략"""
        await self._handle_boss_command(ctx, '카양겔', difficulty)

    @boss.command(name='상아탑', aliases=['탑'])
    async def tower(self, ctx: commands.Context, difficulty: Optional[str] = None):
        """상아탑 공략"""
        await self._handle_boss_command(ctx, '상아탑', difficulty)

    # ==================== 카제로스 레이드 ====================
    @boss.command(name='에키드나', aliases=['에키'])
    async def ekidna(self, ctx: commands.Context, difficulty: Optional[str] = None):
        """에키드나 공략"""
        await self._handle_boss_command(ctx, '에키드나', difficulty)

    @boss.command(name='에기르', aliases=['에기', '기르'])
    async def aegir(self, ctx: commands.Context, difficulty: Optional[str] = None):
        """에기르 공략"""
        await self._handle_boss_command(ctx, '에기르', difficulty)

    @boss.command(name='진아브렐슈드', aliases=['진아브'])
    async def true_abrelshud(self, ctx: commands.Context, difficulty: Optional[str] = None):
        """진아브렐슈드 공략"""
        await self._handle_boss_command(ctx, '진아브렐슈드', difficulty)

    @boss.command(name='모르둠')
    async def mordum(self, ctx: commands.Context, difficulty: Optional[str] = None):
        """모르둠 공략"""
        await self._handle_boss_command(ctx, '모르둠', difficulty)


async def setup(bot):
    """Cog 등록"""
    await bot.add_cog(BossStrategyCog(bot))
