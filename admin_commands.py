
"""
Команды администраторов
"""

import discord
from discord.ext import commands
from datetime import datetime

class AdminCommands(commands.Cog):
    """Ког команд администратора"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="админ")
    @commands.has_permissions(administrator=True)
    async def admin_cmd(self, ctx: commands.Context):
        """Админ панель"""
        stats = self.bot.db.get_stats()
        
        embed = discord.Embed(
            title="⚙️ Админ панель",
            description=f"Управление семьей {self.bot.config.family_name}",
            color=self.bot.config.hex_to_int(self.bot.config.danger_color)
        )
        
        embed.add_field(name="👥 Членов", value=str(stats['total_members']), inline=True)
        embed.add_field(name="📨 Заявок", value=str(stats['pending_applications']), inline=True)
        embed.add_field(name="⚠️ Варнов", value=str(stats['total_warnings']), inline=True)
        
        embed.add_field(
            name="📋 Команды:",
            value=f"• `{self.bot.config.bot_prefix}заявки` - Просмотр заявок\n• `{self.bot.config.bot_prefix}принять @user` - Принять заявку\n• `{self.bot.config.bot_prefix}отклонить @user причина` - Отклонить заявку\n• `{self.bot.config.bot_prefix}предупредить @user причина` - Выдать варн",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="предупредить")
    @commands.has_permissions(administrator=True)
    async def warn_cmd(self, ctx: commands.Context, member: discord.Member, *, reason: str = "Причина не указана"):
        """Выдать предупреждение"""
        # Проверяем является ли участник членом
        member_data = self.bot.db.get_member(str(member.id))
        
        if not member_data:
            embed = discord.Embed(
                title="❌ Ошибка",
                description=f"{member.mention} не является членом семьи!",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        # Добавляем предупреждение
        self.bot.db.add_warning(str(member.id), str(ctx.author.id), reason)
        
        # Считаем количество предупреждений
        warnings = self.bot.db.data['warnings'].get(str(member.id), [])
        warn_count = len(warnings)
        
        embed = discord.Embed(
            title="⚠️ Предупреждение выдано",
            description=f"{member.mention} получил предупреждение!",
            color=0xffa500
        )
        
        embed.add_field(name="Причина", value=reason, inline=False)
        embed.add_field(name="Всего предупреждений", value=str(warn_count), inline=True)
        embed.add_field(name="Лимит", value=str(self.bot.config.warn_limit), inline=True)
        
        await ctx.send(embed=embed)
        
        # Отправляем личное сообщение
        try:
            dm_embed = discord.Embed(
                title="⚠️ ВЫ ПОЛУЧИЛИ ПРЕДУПРЕЖДЕНИЕ",
                description=f"На сервере **{ctx.guild.name}** вам выдано предупреждение.",
                color=0xff0000
            )
            dm_embed.add_field(name="Причина", value=reason, inline=False)
            dm_embed.add_field(name="Выдал", value=str(ctx.author), inline=False)
            dm_embed.add_field(name="Всего предупреждений", value=str(warn_count), inline=True)
            
            await member.send(embed=dm_embed)
        except:
            pass
    
    @commands.command(name="создать_ранг")
    @commands.has_permissions(administrator=True)
    async def create_rank(self, ctx: commands.Context, *, rank_name: str):
        """Создать новый ранг"""
        # Проверяем существование
        ranks = self.bot.db.data['ranks']
        for rank in ranks.values():
            if rank.get('name') == rank_name:
                await ctx.send("❌ Этот ранг уже существует!")
                return
        
        # Создаем новый ранг
        rank_id = f"rank_{len(ranks) + 1}"
        ranks[rank_id] = {
            'name': rank_name,
            'color': self.bot.config.hex_to_int(self.bot.config.primary_color),
            'created_by': str(ctx.author),
            'created_at': datetime.now().isoformat()
        }
        
        self.bot.db._save_file('ranks')
        
        # Пытаемся создать роль в Discord
        try:
            role = await ctx.guild.create_role(
                name=rank_name,
                color=discord.Color(self.bot.config.hex_to_int(self.bot.config.primary_color)),
                mentionable=True
            )
            await ctx.send(f"✅ Ранг '{rank_name}' создан! Роль создана: {role.mention}")
        except Exception as e:
            await ctx.send(f"✅ Ранг '{rank_name}' создан в базе данных!\n(Ошибка создания роли: {e})")

async def setup(bot):
    """Установка кога"""
    await bot.add_cog(AdminCommands(bot))