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
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        #Checks if user invoke any command from cog officers
        if ctx.invoked_with in [str(each_command) for each_command in bot.commands if str(each_command.cog_name) == "Officers"]:
            ctx.channel("Only officers can invoke this command!")
    elif isinstance(error, commands.MissingPermissions):
        #Checks if the command is in cog Admin
        if ctx.invoked_with in [str(each_command.name) for each_command in bot.commands if str(each_command.cog_name) == "Admin"]:
            if ctx.invoked_with == "clear":
                await ctx.channel.purge(limit=1)
            await ctx.channel.send(f"You are not an admin!")

@bot.event
async def on_message(message):
    #=========================Handler if a bot tried to send a command=========================
    try:
        #=========================Making Sure that game channels exist=========================
        if not get(message.guild.categories, name="Palaro"):
            await message.guild.create_category("Palaro")

        game_room_category = get(message.guild.categories, name="Palaro")

        if not get(message.guild.channels, name="guess-the-number"):
            from palaro.gtn.models import GuessTheNumber
            game_room_channel = await message.guild.create_text_channel("guess-the-number", category=game_room_category)
            #=========================Send rules at the top of the channel=========================
            bot_response = GuessTheNumber(message).rules
            for response in bot_response:
                await game_room_channel.send(f"```\n{response}```")

        #=========================Checking the message if it is sent in categories palaro=========================
        if message.channel.category == game_room_category:
            #=========================Make sure that the message is not from the bot=========================
            if message.author.id != 766276001004781568:
                #=========================Message sent in palaro category=========================

                #=========================Handler if a bot tried to send a command=========================
                try:
                    #=========================Checks if the message is a command=========================
                    if message.content.split()[0][0] == ">":
                        await message.channel.purge(limit=1)

                        #=========================Handler if a user or bot can not be DMed=========================
                        try:
                            await message.author.send(f"```\nInvoking of commands is {message.channel.name} is prohibited!```")
                        except discord.errors.HTTPException():
                            pass

                        return
                except IndexError:
                    await message.channel.purge(limit=1)
                    return

                #=========================Message will now be processed by the game=========================
                if message.channel.name == "guess-the-number":
                    from palaro.gtn.models import GuessTheNumber
                    bot_response, instant_response = GuessTheNumber(message).user_response(message)

                #=========================Bot Responds to user that the game's ready=========================
                for response in instant_response:
                    #=========================Handler if a user or bot can not be DMed=========================
                    try:
                        await response
                    except discord.errors.HTTPException():
                        pass
                for response in bot_response:
                    await message.channel.send(f"{message.author.mention}\n```\n{response}```")

        else:
            #=========================Message not sent in palaro category=========================
            await bot.process_commands(message)
    except AttributeError:
        return