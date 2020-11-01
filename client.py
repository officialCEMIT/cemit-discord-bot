import os
import discord
from discord import Client, Intents
from discord.utils import get
from decouple import config

from discord.ext import commands
from discord.ext.commands import Bot, has_permissions, is_owner, errors as d_errors


import git
r = git.Repo.init('')
reader = r.config_reader()
dev = reader.get_value("user","name")

# Permissions bot
intents = Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='>', intents=intents)

CHANNEL_MAP = {
    'bot': '🤖cemit-discord-bot',
    'valid': '✅validation'
}

@bot.command()
async def hello(ctx):
    member = f"<@{ctx.author.id}>"
    await ctx.channel.send(f"Hello {member} :)")

@bot.command()
@is_owner()
async def close(ctx):
    bot_channel = get(bot.get_all_channels(), name=CHANNEL_MAP['bot'])
    await bot_channel.send(f"({dev}) Force closing BOT, bye bye")

    os._exit(1)

@bot.event
async def on_ready():
    print(f"DISCORD {bot.user.name}(BOT) Ready!")
    bot_channel = get(bot.get_all_channels(), name=CHANNEL_MAP['bot'])
    msg = "I'm Online!"

    if dev:
        await bot_channel.send(msg := (f"({dev}) {msg}")) 
    else:
        await bot_channel.send(msg)

@bot.event
async def on_member_join(member):
    role = get(member.guild.roles, name='UNVALIDATED')
    await member.add_roles(role)
    