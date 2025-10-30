import os
import discord
from discord.ext import commands
from discord import app_commands, Intents, Interaction, Embed, ui
from discord.ext.commands import has_permissions, Bot, Context
from datetime import timedelta

TOKEN = os.environ["TOKEN"]
GUILD_ID = None  # Можно ускорить регистрацию команд, установив ID сервера

intents = Intents.all()
intents.message_content = True
intents.members = True

bot = Bot(command_prefix="!", intents=intents)
tree = bot.tree

welcome_settings = {
    "enabled": True,
    "channel": None,
    "text": "Добро пожаловать, {member}!",
    "color": discord.Color.blurple(),
    "banner_url": None
}
autorole_id = None

# ------ КРАСИВЫЕ ВСТАВКИ ------
def make_welcome_embed(member):
    embed = Embed(description=welcome_settings['text'].format(member=member.mention), color=welcome_settings['color'])
    if welcome_settings.get('banner_url'):
        embed.set_image(url=welcome_settings['banner_url'])
    embed.set_footer(text=f"Рады видеть тебя, {member.display_name}!")
    return embed

# -------- /help и /info --------
@tree.command(name="помощь", description="Показать все доступные команды.")
async def help_cmd(inter: Interaction):
    embed = Embed(title="Меню команд Афродизиак Бот", description="Список команд:", color=discord.Color.blurple())
    embed.add_field(name="/бан", value="Забанить участника", inline=False)
    embed.add_field(name="/мут", value="Замутить участника на время", inline=False)
    embed.add_field(name="/анмут", value="Снять мут", inline=False)
    embed.add_field(name="/кик", value="Выгнать участника", inline=False)
    embed.add_field(name="/выдать_роль", value="Выдать роль", inline=False)
    embed.add_field(name="/удалить_роль", value="Удалить роль у участника", inline=False)
    embed.add_field(name="/написать", value="Бот напишет выбранный текст", inline=False)
    embed.add_field(name="/приветствие", value="Настроить приветствие", inline=False)
    embed.add_field(name="/автороль", value="Настроить автороль", inline=False)
    await inter.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="инфо", description="Информация о боте.")
async def info_cmd(inter: Interaction):
    embed = Embed(
        title="Афродизиак | Бот проекта GHOST UNTURNED",
        description="Бот для модерации, приветствий, авторолей и управления сервером Discord.\n\nАвтор: Амиока\nDiscord: amioka11",
        color=discord.Color.blurple()
    )
    await inter.response.send_message(embed=embed, ephemeral=True)

# -------- Обычные текстовые команды с reply --------
@bot.command(name="мут")
@has_permissions(moderate_members=True)
async def mute_legacy(ctx: Context, minutes: int = 10, *, причина: str = ""):
    if ctx.message.reference:
        replied_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        member = replied_msg.author
        until = discord.utils.utcnow() + timedelta(minutes=minutes)
        try:
            await member.timeout(until, reason=причина or "Мут")
            await ctx.send(f"{member.mention} замучен на {minutes} минут. Причина: {причина}")
        except Exception as e:
            await ctx.send(f"Ошибка: {e}")
    else:
        await ctx.send("Ответьте на сообщение пользователя, которого хотите замутить.")

@bot.command(name="анмут")
@has_permissions(moderate_members=True)
async def unmute_legacy(ctx: Context):
    if ctx.message.reference:
        replied_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        member = replied_msg.author
        try:
            await member.timeout(None, reason="Анмут")
            await ctx.send(f"Мут с {member.mention} снят!")
        except Exception as e:
            await ctx.send(f"Ошибка: {e}")
    else:
        await ctx.send("Ответьте на сообщение пользователя, которому нужно снять мут.")

@bot.command(name="кик")
@has_permissions(kick_members=True)
async def kick_legacy(ctx: Context, *, причина: str = ""):
    if ctx.message.reference:
        replied_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        member = replied_msg.author
        try:
            await member.kick(reason=причина or "Кик")
            await ctx.send(f"{member.mention} исключён с сервера. Причина: {причина}")
        except Exception as e:
            await ctx.send(f"Ошибка: {e}")
    else:
        await ctx.send("Ответьте на сообщение пользователя для кика.")

@bot.command(name="бан")
@has_permissions(ban_members=True)
async def ban_legacy(ctx: Context, *, причина: str = ""):
    if ctx.message.reference:
        replied_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        member = replied_msg.author
        try:
            await member.ban(reason=причина or "Бан")
            await ctx.send(f"{member.mention} забанен. Причина: {причина}")
        except Exception as e:
            await ctx.send(f"Ошибка: {e}")
    else:
        await ctx.send("Ответьте на сообщение пользователя для бана.")

# -------- Слэш-модерация --------
@tree.command(name="бан", description="Забанить пользователя с сервера")
@app_commands.describe(участник="Кого забанить", причина="Причина бана")
@has_permissions(ban_members=True)
async def ban(inter: Interaction, участник: discord.Member, причина: str = "Нарушение правил"): 
    await участник.ban(reason=причина)
    await inter.response.send_message(f"Пользователь {участник.mention} забанен. Причина: {причина}")

@tree.command(name="кик", description="Выгнать пользователя с сервера")
@app_commands.describe(участник="Кого кикнуть", причина="Причина")
@has_permissions(kick_members=True)
async def kick(inter: Interaction, участник: discord.Member, причина: str = "Нарушение правил"): 
    await участник.kick(reason=причина)
    await inter.response.send_message(f"Пользователь {участник.mention} кикнут. Причина: {причина}")

@tree.command(name="мут", description="Замутить пользователя на X минут")
@app_commands.describe(участник="Кого замутить", минуты="На сколько минут", причина="Причина")
@has_permissions(moderate_members=True)
async def mute(inter: Interaction, участник: discord.Member, минуты: int = 10, причина: str = ""): 
    until = discord.utils.utcnow() + timedelta(minutes=минуты)
    await участник.timeout(until, reason=причина or "Мут")
    await inter.response.send_message(f"{участник.mention} замучен на {минуты} минут. Причина: {причина}")

@tree.command(name="анмут", description="Снять мут с пользователя")
@app_commands.describe(участник="С кого снять мут")
@has_permissions(moderate_members=True)
async def unmute(inter: Interaction, участник: discord.Member):
    await участник.timeout(None, reason="Анмут")
    await inter.response.send_message(f"Мут с {участник.mention} снят!")

# -------- /написать --------
@tree.command(name="написать", description="Заставить бота написать сообщение от вашего имени.")
@app_commands.describe(текст="Текст для отправки")
@has_permissions(administrator=True)
async def say(inter: Interaction, текст: str):
    await inter.channel.send(текст)
    await inter.response.send_message("Сообщение отправлено!", ephemeral=True)

# -------- /выдать_роль и /удалить_роль --------
@tree.command(name="выдать_роль", description="Выдать роль участнику.")
@app_commands.describe(участник="Кому выдать", роль="Какую роль выдать")
@has_permissions(manage_roles=True)
async def роль_выдать(inter: Interaction, участник: discord.Member, роль: discord.Role):
    try:
        await участник.add_roles(роль, reason=f"Выдано через /выдать_роль {inter.user}")
        await inter.response.send_message(f"{участник.mention} теперь с ролью {роль.mention}.")
    except Exception as e:
        await inter.response.send_message(f"Ошибка: {e}", ephemeral=True)

@tree.command(name="удалить_роль", description="Удалить роль у участника.")
@app_commands.describe(участник="У кого убрать", роль="Какую роль удалить")
@has_permissions(manage_roles=True)
async def роль_удалить(inter: Interaction, участник: discord.Member, роль: discord.Role):
    try:
        await участник.remove_roles(роль, reason=f"Удалено через /удалить_роль {inter.user}")
        await inter.response.send_message(f"{роль.mention} убрана у {участник.mention}.")
    except Exception as e:
        await inter.response.send_message(f"Ошибка: {e}", ephemeral=True)

# -------- Приветствие и Автороль --------
@tree.command(name="приветствие", description="Настроить приветствие для новых участников.")
@app_commands.describe(включить="Вкл/выкл приветствие", текст="Текст приветствия", цвет="HEX-цвет (#RRGGBB)", баннер_url="URL-баннера", канал="Канал для приветствий")
@has_permissions(administrator=True)
async def приветствие(inter: Interaction, включить: bool = True, текст: str = None, цвет: str = None, баннер_url: str = None, канал: discord.TextChannel = None):
    welcome_settings['enabled'] = включить
    if текст: welcome_settings['text'] = текст
    if цвет:
        try:
            welcome_settings['color'] = discord.Color(int(цвет.replace('#',''), 16))
        except:
            pass
    if баннер_url: welcome_settings['banner_url'] = баннер_url
    if канал: welcome_settings['channel'] = канал.id
    await inter.response.send_message("Настройки приветствия успешно обновлены!", ephemeral=True)

@tree.command(name="автороль", description="Назначить автороль для новых участников.")
@app_commands.describe(роль="Выберите автороль (None чтоб выключить)")
@has_permissions(administrator=True)
async def автороль(inter: Interaction, роль: discord.Role = None):
    global autorole_id
    if роль:   autorole_id = роль.id
    else:     autorole_id = None
    await inter.response.send_message(f"Автороль обновлена: {роль.mention if роль else 'автороль выключена'}", ephemeral=True)

@bot.event
async def on_member_join(member: discord.Member):
    if welcome_settings.get('enabled'):
        channel_id = welcome_settings.get('channel')
        channel = member.guild.get_channel(channel_id) if channel_id else None or next((c for c in member.guild.text_channels if c.permissions_for(member.guild.me).send_messages), None)
        embed = make_welcome_embed(member)
        await channel.send(embed=embed)
    if autorole_id:
        role = member.guild.get_role(autorole_id)
        if role:
            await member.add_roles(role, reason="Автороль по вступлению")

# -------- READY & SYNC --------
@bot.event
async def on_ready():
    print(f"Бот запущен как {bot.user}")
    try:
        synced = await tree.sync(guild=discord.Object(id=GUILD_ID)) if GUILD_ID else await tree.sync()
        print(f"Slash-команды синхронизированы: {len(synced)}")
    except Exception as e:
        print(f"Ошибка синхронизации команд: {e}")

bot.run(TOKEN)
