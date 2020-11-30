import os
import discord
from discord import Client, Intents
from discord.utils import get
from decouple import config

from discord.ext import commands
from discord.ext.commands import Bot, has_permissions, is_owner, errors as d_errors

from os.path import exists
from os import remove
import sqlite3


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
    user_id = int(message.author.id)
    try:
        channel_category = str(message.channel.category)
    except AttributeError:
        return

    if channel_category == "Games":
        if user_id != 773355955587907584:
            game_folder = "#" + str(message.guild.id)
            game_room_id = str(message.channel.id)
            path = f"services/games/{game_folder}/{game_room_id}.json"

            #Checks if the user is the one who is trying to communicate with the bot in the game room
            guild_game_data = sqlite3.connect(f"services/games/#{message.guild.id}/guild_game_data.db")
            active_rooms = guild_game_data.cursor()
            active_rooms.execute("SELECT users_id FROM activerooms WHERE channel_id = '{}'".format(message.channel.id))
            fetched_users_id = active_rooms.fetchall()
            guild_game_data.commit()
            guild_game_data.close()
            for each_active_room in fetched_users_id:
                if str(user_id) not in each_active_room:
                    await message.channel.purge(limit=1)
                    try:
                        await message.author.send(f"```Sorry, you are not allowed to send messages in game room {message.channel.name}.```")
                    except:
                        pass
                    else:
                        return

            #Sets the game of the user
            game_room_game_index = int(message.channel.name.split('-')[0])
            if game_room_game_index == 1:
                from services.games.lib.GuessTheNumber import GuessTheNumber
                game_library = GuessTheNumber()
            #Checks the message if it has game command
            if message.content[:2] == "--":
                #Gets the command of the user
                game_command = message.content.split(" ")[0][2].lower()
                try:
                    game_command_params = message.content.lower().split(" ")[1:]
                except:
                    game_command_params = []

                #Checks the game command invoked by the user
                if game_command == "p":
                    bot_response = game_library.start_game(game_command_params, path, str(user_id))
                    for response in bot_response:
                        await message.channel.send(response)
                elif game_command == "h":
                    await message.channel.send(game_library.game_help)
                elif game_command == "s":
                    pass
                elif game_command == "q":
                    #Deletes the game room
                    await message.channel.send("```\nGoodbye!```")
                    await message.channel.category.set_permissions(message.author, read_messages=False, send_messages=False)
                    await asyncio.sleep(1)
                    await message.channel.delete()

                    #Erases the room from list of active rooms
                    guild_game_data = sqlite3.connect(f"services/games/#{message.guild.id}/guild_game_data.db")
                    active_rooms = guild_game_data.cursor()
                    active_rooms.execute("DELETE FROM activerooms WHERE users_id = '{}'".format(user_id))
                    guild_game_data.commit()
                    guild_game_data.close()
                    if exists(path):
                        remove(path)
                else:
                    await message.channel.send(f"```\nSorry, there is no action as {game_command}.```")
            else:
                with open("prefixes.json", "r") as f:
                    prefixes = json.load(f)
                try:
                    if message.content[0] == prefixes[str(guild_id)]:
                        await message.channel.purge(limit=1)
                        await message.channel.send("```\nNo invoking of commands except game commands in here!```")
                    elif exists(path):
                        bot_response = game_library.user_response(message, path, str(user_id))
                        if bot_response:
                            for response in bot_response:
                                await message.channel.send(response)
                except IndexError:
                    await message.channel.purge(limit=1)
                    await message.channel.send("```\nNo invoking of commands except game commands in here!```")
    else:
        await bot.process_commands(message)