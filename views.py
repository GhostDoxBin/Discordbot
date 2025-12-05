"""
View элементы для бота
"""

import discord
from discord.ui import View, Button
from database.family_db import FamilyDB

class ApplicationModal(discord.ui.Modal):
    """Модальное окно заявки"""
    def __init__(self, config, db: FamilyDB):
        super().__init__(title=f"📋 Заявка в {config.family_name}")
        self.config = config
        self.db = db
        
        self.age = discord.ui.TextInput(
            label="Ваш возраст",
            placeholder=f"Введите возраст (от {config.min_age} лет)",
            required=True,
            max_length=3
        )
        
        self.level = discord.ui.TextInput(
            label="Уровень в игре",
            placeholder=f"Введите уровень (от {config.min_level})",
            required=True,
            max_length=3
        )
        
        self.game_name = discord.ui.TextInput(
            label="Игровой ник",
            placeholder="Введите ваш игровой ник",
            required=True,
            max_length=50
        )
        
        self.experience = discord.ui.TextInput(
            label="Игровой опыт",
            placeholder="Расскажите о вашем игровом опыте...",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=500
        )
        
        self.reason = discord.ui.TextInput(
            label="Почему хотите вступить?",
            placeholder="Почему хотите вступить в нашу семью?",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=500
        )
        
        self.add_item(self.age)
        self.add_item(self.level)
        self.add_item(self.game_name)
        self.add_item(self.experience)
        self.add_item(self.reason)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            age = int(self.age.value)
            level = int(self.level.value)
            
            if age < self.config.min_age:
                await interaction.response.send_message(
                    f"❌ Минимальный возраст - {self.config.min_age} лет.",
                    ephemeral=True
                )
                return
            
            if level < self.config.min_level:
                await interaction.response.send_message(
                    f"❌ Минимальный уровень - {self.config.min_level}.",
                    ephemeral=True
                )
                return
            
            # Проверяем, не подана ли уже заявка
            existing_app = self.db.data['applications'].get(str(interaction.user.id))
            if existing_app and existing_app.get('status') == 'pending':
                await interaction.response.send_message(
                    "📝 Ваша заявка уже на рассмотрении!",
                    ephemeral=True
                )
                return
            
            # Сохраняем заявку
            application_data = {
                'user_id': str(interaction.user.id),
                'username': str(interaction.user),
                'full_name': interaction.user.display_name,
                'age': age,
                'level': level,
                'game_name': self.game_name.value,
                'experience': self.experience.value,
                'reason': self.reason.value,
                'status': 'pending'
            }
            
            self.db.add_application(str(interaction.user.id), application_data)
            
            await interaction.response.send_message(
                "✅ Заявка отправлена!\nОжидайте решения администрации.",
                ephemeral=True
            )
            
        except ValueError:
            await interaction.response.send_message(
                "❌ Пожалуйста, введите корректные числа для возраста и уровня!",
                ephemeral=True
            )

class Views:
    """Класс для View элементов"""
    
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config
        self.db = bot.db
    
    def main_menu_view(self, is_admin: bool = False) -> View:
        """Главное меню"""
        view = View(timeout=60)
        
        # Кнопка подачи заявки
        apply_button = Button(label="📋 Подать заявку", style=discord.ButtonStyle.success)
        
        async def apply_callback(interaction: discord.Interaction):
            # Проверяем, не является ли уже членом
            if self.db.get_member(str(interaction.user.id)):
                await interaction.response.send_message(
                    "✅ Вы уже член семьи!",
                    ephemeral=True
                )
                return
            
            modal = ApplicationModal(self.config, self.db)
            await interaction.response.send_modal(modal)
        
        apply_button.callback = apply_callback
        view.add_item(apply_button)
        
        # Кнопка статистики
        stats_button = Button(label="📊 Статистика", style=discord.ButtonStyle.primary)
        
        async def stats_callback(interaction: discord.Interaction):
            stats = self.db.get_stats()
            
            from ui.embeds import Embeds
            embeds = Embeds(self.config)
            
            embed = discord.Embed(
                title=f"📊 Статистика семьи {self.config.family_name}",
                color=self.config.hex_to_int(self.config.info_color)
            )
            
            embed.add_field(name="👥 Членов", value=str(stats['total_members']), inline=True)
            embed.add_field(name="📨 Заявок", value=str(stats['pending_applications']), inline=True)
            embed.add_field(name="⚠️ Варнов", value=str(stats['total_warnings']), inline=True)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        stats_button.callback = stats_callback
        view.add_item(stats_button)
        
        # Кнопка членов
        members_button = Button(label="👥 Члены", style=discord.ButtonStyle.secondary)
        
        async def members_callback(interaction: discord.Interaction):
            members = self.db.get_all_members()
            
            if not members:
                await interaction.response.send_message(
                    "👥 В семье пока нет членов.",
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title=f"👥 Члены семьи {self.config.family_name}",
                color=self.config.hex_to_int(self.config.info_color)
            )
            
            for i, (user_id, member) in enumerate(list(members.items())[:10], 1):
                embed.add_field(
                    name=f"{i}. {member.get('game_name', 'Без имени')}",
                    value=f"🎖️ {member.get('rank', 'Новичок')}",
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        members_button.callback = members_callback
        view.add_item(members_button)
        
        # Кнопка профиля
        profile_button = Button(label="👤 Профиль", style=discord.ButtonStyle.success)
        
        async def profile_callback(interaction: discord.Interaction):
            member_data = self.db.get_member(str(interaction.user.id))
            
            from ui.embeds import Embeds
            embeds = Embeds(self.config)
            
            if member_data:
                embed = embeds.profile_embed(interaction.user, member_data)
                # Добавляем варны
                warnings = self.db.data['warnings'].get(str(interaction.user.id), [])
                if warnings:
                    embed.add_field(
                        name="⚠️ Предупреждения",
                        value=f"Всего: {len(warnings)}",
                        inline=True
                    )
            else:
                embed = discord.Embed(
                    title=f"👤 {interaction.user.display_name}",
                    description="❌ Не является членом семьи",
                    color=self.config.hex_to_int(self.config.danger_color)
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        profile_button.callback = profile_callback
        view.add_item(profile_button)
        
        # Кнопка правил
        rules_button = Button(label="📜 Правила", style=discord.ButtonStyle.secondary)
        
        async def rules_callback(interaction: discord.Interaction):
            embed = discord.Embed(
                title=f"📜 Правила семьи {self.config.family_name}",
                color=self.config.hex_to_int(self.config.warning_color)
            )
            
            rules = [
                "1. Уважение к каждому члену семьи",
                "2. Активность в играх и общении",
                "3. Помощь новичкам и поддержка товарищей",
                "4. Исполнение приказов руководства"
            ]
            
            embed.description = "\n".join(rules)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        rules_button.callback = rules_callback
        view.add_item(rules_button)
        
        # Кнопка для админов
        if is_admin:
            admin_button = Button(label="⚙️ Админ", style=discord.ButtonStyle.danger)
            
            async def admin_callback(interaction: discord.Interaction):
                stats = self.db.get_stats()
                
                embed = discord.Embed(
                    title="⚙️ Админ панель",
                    color=self.config.hex_to_int(self.config.danger_color)
                )
                
                embed.add_field(name="👥 Членов", value=str(stats['total_members']), inline=True)
                embed.add_field(name="📨 Заявок", value=str(stats['pending_applications']), inline=True)
                embed.add_field(name="⚠️ Варнов", value=str(stats['total_warnings']), inline=True)
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
            
            admin_button.callback = admin_callback
            view.add_item(admin_button)
        
        return view