"""
Команды для работы с заявками
"""

import discord
from discord.ext import commands
from datetime import datetime

class ApplicationCommands(commands.Cog):
    """Ког команд для заявок"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="заявки")
    @commands.has_permissions(administrator=True)
    async def applications_cmd(self, ctx: commands.Context):
        """Просмотр заявок"""
        apps = self.bot.db.get_pending_applications()
        
        if not apps:
            embed = discord.Embed(
                title="📨 Заявки",
                description="Нет заявок на рассмотрении.",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title="📨 Заявки на рассмотрении",
            color=0xffa500
        )
        
        for i, app in enumerate(apps[:5], 1):
            embed.add_field(
                name=f"{i}. {app.get('full_name', app.get('username', 'Без имени'))}",
                value=f"🎂 Возраст: {app.get('age')}\n🎮 Уровень: {app.get('level')}\n🎮 Ник: {app.get('game_name')}\n\nИспользуйте:\n`!принять {app.get('user_id')} ранг`\n`!отклонить {app.get('user_id')} причина`",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="принять")
    @commands.has_permissions(administrator=True)
    async def accept_cmd(self, ctx: commands.Context, user_id: str, rank: str = "Новичок"):
        """Принять заявку"""
        # Проверяем заявку
        applications = self.bot.db.data['applications']
        
        if user_id not in applications:
            embed = discord.Embed(
                title="❌ Ошибка",
                description="Заявка не найдена!",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        application = applications[user_id]
        
        # Добавляем в члены
        member_data = {
            'user_id': user_id,
            'username': application.get('username', ''),
            'full_name': application.get('full_name', ''),
            'game_name': application.get('game_name', ''),
            'rank': rank,
            'join_date': datetime.now().isoformat(),
            'level': application.get('level', 0),
            'age': application.get('age', 0)
        }
        
        self.bot.db.add_member(user_id, member_data)
        
        # Обновляем статус заявки
        applications[user_id]['status'] = 'accepted'
        self.bot.db._save_file('applications')
        
        # Пытаемся найти пользователя и уведомить
        try:
            member = ctx.guild.get_member(int(user_id))
            if member:
                # Пытаемся выдать роль
                role_name = rank
                role = discord.utils.get(ctx.guild.roles, name=role_name)
                
                if role:
                    await member.add_roles(role)
                
                # Отправляем сообщение
                embed = discord.Embed(
                    title="🎉 ПОЗДРАВЛЯЕМ!",
                    description=f"Ваша заявка в семью **{self.bot.config.family_name}** принята!",
                    color=0x00ff00
                )
                embed.add_field(name="🎖️ Ваш ранг", value=rank, inline=False)
                embed.add_field(name="✅ Принял", value=str(ctx.author), inline=False)
                
                await member.send(embed=embed)
        except Exception as e:
            print(f"Ошибка при принятии заявки: {e}")
        
        embed = discord.Embed(
            title="✅ Заявка принята",
            description=f"Пользователь {application.get('full_name', user_id)} принят в семью с рангом {rank}!",
            color=0x00ff00
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="отклонить")
    @commands.has_permissions(administrator=True)
    async def reject_cmd(self, ctx: commands.Context, user_id: str, *, reason: str = "Причина не указана"):
        """Отклонить заявку"""
        applications = self.bot.db.data['applications']
        
        if user_id not in applications:
            embed = discord.Embed(
                title="❌ Ошибка",
                description="Заявка не найдена!",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        # Обновляем статус
        applications[user_id]['status'] = 'rejected'
        applications[user_id]['reject_reason'] = reason
        self.bot.db._save_file('applications')
        
        # Пытаемся уведомить пользователя
        try:
            member = ctx.guild.get_member(int(user_id))
            if member:
                embed = discord.Embed(
                    title="😔 ЗАЯВКА ОТКЛОНЕНА",
                    description=f"Ваша заявка в семью **{self.bot.config.family_name}** отклонена.",
                    color=0xff0000
                )
                embed.add_field(name="📝 Причина", value=reason, inline=False)
                
                await member.send(embed=embed)
        except:
            pass
        
        embed = discord.Embed(
            title="❌ Заявка отклонена",
            description=f"Заявка пользователя {user_id} отклонена.\nПричина: {reason}",
            color=0xff0000
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    """Установка кога"""
    await bot.add_cog(ApplicationCommands(bot))