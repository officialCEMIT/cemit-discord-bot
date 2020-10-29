import discord
from discord import Client, Intents
from discord.utils import get
from decouple import config

from discord.ext import commands
from discord.ext.commands import Bot

from .core.api import CEMIT
from .core.errors import MemberExists, MemberNotFound

# Permissions bot
intents = Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='>', intents=intents)

cemit = CEMIT()

CHANNEL_MAP = {
    'bot': '🤖cemit-discord-bot',
    'valid': '✅validation'
}


@bot.command()
async def validate(ctx, user_id):
    if ctx.channel.name == CHANNEL_MAP['valid']:
        """
        TODO: 
            - Check id in DB
            - Check if already validated
        """
        try:
            cemit.validate_member(user_id)
            role = get(ctx.author.guild.roles, name='MEMBER')
            await ctx.author.add_roles(role)
            await ctx.author.remove_roles(get(ctx.author.guild.roles, name='UNVALIDATED'))
            #TODO: REMOVE UNVALIDATED
            await ctx.channel.send("Successfully Validated")
        except MemberExists:
            await ctx.channel.send("The CEMIT member ID you sent is already exists here")
            await ctx.channel.send("If you think this is a mistake, @ an online officer to assist you")
        except MemberNotFound:
            await ctx.channel.send("The ID you sent does not match any of the CEMIT members registered")
            await ctx.channel.send("If you think this is a mistake, @ an online officer to assist you")


@bot.command()
async def hello(ctx):
    member = f"<@{ctx.author.id}>"
    await ctx.channel.send(f"Hello {member} :)")


@bot.event
async def on_ready():
    print(f"DISCORD {bot.user.name}(BOT) Ready!")
    bot_channel = get(bot.get_all_channels(), name=CHANNEL_MAP['bot'])
    msg = "I'm Online!"
    if (dev := config('DEV', "")):
        await bot_channel.send(msg := (f"({dev}) {msg}")) 
    else:
        await bot_channel.send(msg)

@bot.event
async def on_member_join(member):
    role = get(member.guild.roles, name='UNVALIDATED')
    await member.add_roles(role)
    
