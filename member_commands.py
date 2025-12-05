
"""
Команды для членов семьи
"""

import discord
from discord.ext import commands
from datetime import datetime

class MemberCommands(commands.Cog):
    """Ког команд для членов"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="профиль")
    async def profile_cmd(self, ctx: commands.Context, member: discord.Member = None):
        """Просмотр профиля"""
        target = member or ctx.author
        
        # Получаем данные из базы
        member_data = self.bot.db.get_member(str(target.id))
        
        if not member_data:
            embed = discord.Embed(
                title="❌ Ошибка",
                description=f"{target.mention} не является членом семьи.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        # Создаем embed профиля
        embed = discord.Embed(
            title=f"👤 Профиль {target.display_name}",
            color=target.color if target.color != discord.Color.default() else self.bot.config.hex_to_int(self.bot.config.primary_color),
            timestamp=datetime.now()
        )
        
        if target.avatar:
            embed.set_thumbnail(url=target.avatar.url)
        
        embed.add_field(name="🎮 Игровой ник", value=member_data.get('game_name', 'Не указан'), inline=True)
        embed.add_field(name="🎖️ Ранг", value=member_data.get('rank', 'Новичок'), inline=True)
        embed.add_field(name="📅 В семье с", value=member_data.get('join_date', 'Недавно')[:10], inline=True)
        embed.add_field(name="🆔 Discord ID", value=target.id, inline=True)
        
        # Добавляем информацию о предупреждениях
        warnings = self.bot.db.data['warnings'].get(str(target.id), [])
        if warnings:
            embed.add_field(
                name="⚠️ Предупреждения",
                value=f"Всего: {len(warnings)}",
                inline=True
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="члены")
    async def members_cmd(self, ctx: commands.Context):
        """Просмотр членов семьи"""
        members = self.bot.db.get_all_members()
        
        if not members:
            await ctx.send("👥 В семье пока нет членов.")
            return
        
        embed = discord.Embed(
            title=f"👥 Члены семьи {self.bot.config.family_name}",
            color=self.bot.config.hex_to_int(self.bot.config.info_color)
        )
        
        for i, (user_id, member) in enumerate(list(members.items())[:10], 1):
            embed.add_field(
                name=f"{i}. {member.get('game_name', 'Без имени')}",
                value=f"🎖️ {member.get('rank', 'Новичок')}",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="правила")
    async def rules_cmd(self, ctx: commands.Context):
        """Правила семьи"""
        embed = discord.Embed(
            title=f"📜 Правила семьи {self.bot.config.family_name}",
            color=self.bot.config.hex_to_int(self.bot.config.warning_color)
        )
        
        rules = [
            "1. Уважение к каждому члену семьи",
            "2. Активность в играх и общении",
            "3. Помощь новичкам и поддержка товарищей",
            "4. Исполнение приказов руководства",
            "5. Конфиденциальность внутренней информации"
        ]
        
        for rule in rules:
            embed.add_field(name="", value=rule, inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.command(name="статистика")
    async def stats_cmd(self, ctx: commands.Context):
        """Статистика семьи"""
        stats = self.bot.db.get_stats()
        
        embed = discord.Embed(
            title=f"📊 Статистика семьи {self.bot.config.family_name}",
            color=self.bot.config.hex_to_int(self.bot.config.info_color),
            timestamp=datetime.now()
        )
        
        embed.add_field(name="👥 Членов", value=str(stats['total_members']), inline=True)
        embed.add_field(name="📨 Заявок", value=str(stats['pending_applications']), inline=True)
        embed.add_field(name="🎖️ Рангов", value=str(stats['total_ranks']), inline=True)
        embed.add_field(name="⚠️ Варнов", value=str(stats['total_warnings']), inline=True)
        embed.add_field(name="📅 Событий", value=str(stats['total_events']), inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command(name="помощь")
    async def help_cmd(self, ctx: commands.Context):
        """Помощь по командам"""
        embed = discord.Embed(
            title="❓ Помощь по командам",
            description=f"Используйте `/` для вызова меню\nПрефикс команд: `{self.bot.config.bot_prefix}`",
            color=self.bot.config.hex_to_int(self.bot.config.info_color)
        )
        
        embed.add_field(
            name="📋 Основные команды:",
            value=f"• `{self.bot.config.bot_prefix}старт` - Главное меню\n• `{self.bot.config.bot_prefix}статистика` - Статистика\n• `{self.bot.config.bot_prefix}члены` - Члены\n• `{self.bot.config.bot_prefix}правила` - Правила\n• `{self.bot.config.bot_prefix}профиль` - Профиль",
            inline=False
        )
        
        if ctx.author.guild_permissions.administrator:
            embed.add_field(
                name="⚙️ Администраторские:",
                value=f"• `{self.bot.config.bot_prefix}админ` - Админ панель\n• `{self.bot.config.bot_prefix}заявки` - Заявки\n• `{self.bot.config.bot_prefix}принять` - Принять заявку\n• `{self.bot.config.bot_prefix}отклонить` - Отклонить заявку",
                inline=False
            )
        
        embed.set_footer(text=f"Семья {self.bot.config.family_name}")
        await ctx.send(embed=embed)

async def setup(bot):
    """Установка кога"""
    await bot.add_cog(MemberCommands(bot))