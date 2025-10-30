import os
import discord
from discord.ext import commands
from discord import app_commands, Intents, Interaction, Embed, ui
from discord.ext.commands import has_permissions, Bot
from datetime import timedelta

TOKEN = os.environ["TOKEN"]
GUILD_ID = None  # Можно указать ID сервера для ускорения регистрации команд

intents = Intents.all()
intents.message_content = True

bot = Bot(command_prefix="!", intents=intents)
tree = bot.tree

log_channel_id = None  # Можно вынести в настройки/БД
welcome_settings = {
    "enabled": True,
    "channel": None,
    "text": "Добро пожаловать, {member}!",
    "color": discord.Color.blurple(),
    "banner_url": None
}
autorole_id = None

# --------- HELP & INFO ---------
@tree.command(name="help", description="Показать все доступные команды.")
async def help_cmd(inter: Interaction):
    embed = Embed(title="Команды GHOST UNTURNED Bot", description="Все доступные slash-команды:", color=discord.Color.blurple())
    embed.add_field(name="/ban [@Юзер] [причина]", value="Забанить участника", inline=False)
    embed.add_field(name="/mute [@Юзер] [минуты] [причина]", value="Заглушить участника", inline=False)
    embed.add_field(name="/unmute [@Юзер]", value="Снять мут", inline=False)
    embed.add_field(name="/timeout [@Юзер] [минуты] [причина]", value="Таймаут участника", inline=False)
    embed.add_field(name="/kick [@Юзер] [причина]", value="Выгнать участника", inline=False)
    embed.add_field(name="/info", value="О боте", inline=False)
    embed.add_field(name="/setting", value="Настройки для админов", inline=False)
    await inter.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="info", description="Информация о боте.")
async def info_cmd(inter: Interaction):
    embed = Embed(
        title="GHOST UNTURNED Bot",
        description="Бот создан для управления сервером GHOST UNTURNED. Поддерживает модерацию, приветствия, автороли и гибкие настройки!\n\nby Amika111",
        color=discord.Color.blurple()
    )
    embed.add_field(name="GitHub", value="https://github.com/Amika111/discord-botik", inline=False)
    await inter.response.send_message(embed=embed, ephemeral=True)

# --------- MODERATION ---------
@tree.command(name="ban", description="Забанить пользователя")
@has_permissions(ban_members=True)
async def ban(inter: Interaction, member: discord.Member, reason: str = "Нарушение правил"): 
    await member.ban(reason=reason)
    await inter.response.send_message(f"Пользователь {member.mention} забанен. Причина: {reason}")
    await send_log(f":no_entry: {inter.user.mention} забанил {member.mention}. Причина: {reason}")

@tree.command(name="kick", description="Выгнать пользователя")
@has_permissions(kick_members=True)
async def kick(inter: Interaction, member: discord.Member, reason: str = "Нарушение правил"): 
    await member.kick(reason=reason)
    await inter.response.send_message(f"Пользователь {member.mention} кикнут. Причина: {reason}")
    await send_log(f":boot: {inter.user.mention} кикнул {member.mention}. Причина: {reason}")

@tree.command(name="mute", description="Мут пользователя на X минут.")
@has_permissions(moderate_members=True)
async def mute(inter: Interaction, member: discord.Member, minutes: int = 10, reason: str = ""): 
    until = discord.utils.utcnow() + timedelta(minutes=minutes)
    await member.timeout(until, reason=reason or "Мут")
    await inter.response.send_message(f"{member.mention} замучен на {minutes} минут. {('Причина: ' + reason) if reason else ''}")
    await send_log(f":mute: {inter.user.mention} замутил {member.mention} на {minutes} мин. {('Причина: ' + reason) if reason else ''}")

@tree.command(name="unmute", description="Снять мут")
@has_permissions(moderate_members=True)
async def unmute(inter: Interaction, member: discord.Member):
    await member.timeout(None, reason="Анмут")
    await inter.response.send_message(f"Мут с {member.mention} снят!")
    await send_log(f":sound: {inter.user.mention} снял мут с {member.mention}")

@tree.command(name="timeout", description="Дать таймаут пользователю на X минут.")
@has_permissions(moderate_members=True)
async def timeout(inter: Interaction, member: discord.Member, minutes: int = 5, reason: str = ""): 
    until = discord.utils.utcnow() + timedelta(minutes=minutes)
    await member.timeout(until, reason=reason or "Таймаут")
    await inter.response.send_message(f"Выдан таймаут {member.mention} на {minutes} минут. {('Причина: ' + reason) if reason else ''}")
    await send_log(f":hourglass: {inter.user.mention} дал таймаут {member.mention} на {minutes} мин. {('Причина: ' + reason) if reason else ''}")

# --------- SETTINGS (ADMIN MENU) ---------
class SettingsView(ui.View):
    def __init__(self, author: discord.User):
        super().__init__(timeout=120)
        self.author = author

    @ui.button(label="Приветствия", style=discord.ButtonStyle.blurple)
    async def welcome_btn(self, interaction: Interaction, button: ui.Button):
        await interaction.response.send_message(f"Настройка приветствий. (Доработаем меню по желанию)", ephemeral=True)

    @ui.button(label="Автороли", style=discord.ButtonStyle.gray)
    async def autorole_btn(self, interaction: Interaction, button: ui.Button):
        await interaction.response.send_message(f"Настройка авторолей. (В разработке)", ephemeral=True)

    @ui.button(label="Логи", style=discord.ButtonStyle.gray)
    async def log_btn(self, interaction: Interaction, button: ui.Button):
        await interaction.response.send_message(f"Настройка логиррования. (В разработке)", ephemeral=True)

    @ui.button(label="Закрыть", style=discord.ButtonStyle.red)
    async def close_btn(self, interaction: Interaction, button: ui.Button):
        await interaction.message.delete()

@tree.command(name="setting", description="Админ-меню для настройки бота.")
@has_permissions(administrator=True)
async def setting(inter: Interaction):
    embed = Embed(title="Меню Настроек GHOST UNTURNED Bot", description="Выберите нужный блок для настройки:", color=discord.Color.orange())
    await inter.response.send_message(embed=embed, view=SettingsView(inter.user), ephemeral=True)

# --------- WELCOME + AUTOROLE ---------
@bot.event
async def on_member_join(member: discord.Member):
    if welcome_settings.get('enabled'):
        channel_id = welcome_settings.get('channel')
        channel = member.guild.get_channel(channel_id) if channel_id else None or next((c for c in member.guild.text_channels if c.permissions_for(member.guild.me).send_messages), None)
        banner = welcome_settings.get('banner_url')
        embed = Embed(description=welcome_settings['text'].format(member=member.mention), color=welcome_settings['color'])
        if banner:
            embed.set_image(url=banner)
        await channel.send(embed=embed)
    if autorole_id:
        role = member.guild.get_role(autorole_id)
        if role:
            await member.add_roles(role, reason="Автороль по вступлению")

# --------- MESSAGE/ROLE/LOG EVENTS ---------
async def send_log(text):
    if log_channel_id:
        ch = bot.get_channel(log_channel_id)
        if ch:
            await ch.send(text)

@bot.event
async def on_message_delete(message):
    await send_log(f"Удалено сообщение {message.author.mention} в <#{message.channel.id}>: {message.content}")

@bot.event
async def on_guild_role_update(before, after):
    await send_log(f"Обновлена роль: {before.name} -> {after.name}")

@bot.event
async def on_member_update(before, after):
    if before.roles != after.roles:
        await send_log(f"Роли пользователя {before.mention} обновлены.")

# --------- READY EVENT & COMMAND SYNC ---------
@bot.event
async def on_ready():
    print(f"Бот запущен как {bot.user}")
    try:
        synced = await tree.sync(guild=discord.Object(id=GUILD_ID)) if GUILD_ID else await tree.sync()
        print(f"Slash-команды синхронизированы: {len(synced)}")
    except Exception as e:
        print(f"Ошибка синхронизации команд: {e}")

bot.run(TOKEN)
