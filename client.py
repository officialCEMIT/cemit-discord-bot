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


@bot.event
async def on_message(message):
    emoji_box = list("🟥🟧🟨🟩🟪🔴🟠🟡🟢🟣")

    if message.content.startswith('/poll'):
        message_body = "" # stores the choices as a message
        choices = message.content[6:].strip().split(',') # gets the choices from the csv

        if len(choices) <= 10: # checks if the choices is within the limit
            for i in range(len(choices)): # builds the message body 
                message_body += f"{emoji_box[i]}:  {choices[i]} \n"
            msg = await message.channel.send(message_body) # sends the message body and store it to a variable

            for i in range(len(choices)):
                await msg.add_reaction(emoji_box[i]) # add the reaction to the message for voting
        else: # Sends alternate message if it is over the limit
            await message.channel.send("The limit is 10 choices only. Please try again.") 