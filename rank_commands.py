
"""
Команды для управления рангами
"""

import discord
from discord.ext import commands
from datetime import datetime

class RankCommands(commands.Cog):
    """Ког команд для рангов"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="ранги")
    async def ranks_cmd(self, ctx: commands.Context):
        """Список рангов"""
        ranks = self.bot.db.data['ranks']
        
        if not ranks:
            embed = discord.Embed(
                title="🎖️ Ранги",
                description="Ранги еще не созданы. Администраторы могут создать их с помощью `!создать_ранг`",
                color=self.bot.config.hex_to_int(self.bot.config.info_color)
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title=f"🎖️ Ранги семьи {self.bot.config.family_name}",
            color=self.bot.config.hex_to_int(self.bot.config.info_color),
            timestamp=datetime.now()
        )
        
        for rank_id, rank_data in ranks.items():
            embed.add_field(
                name=rank_data.get('name', 'Без имени'),
                value=f"Создал: {rank_data.get('created_by', 'Неизвестно')}\nДата: {rank_data.get('created_at', '')[:10]}",
                inline=False
            )
        
        await ctx.send(embed=embed)

async def setup(bot):
    """Установка кога"""
    await bot.add_cog(RankCommands(bot))