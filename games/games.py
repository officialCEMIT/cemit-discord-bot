import discord
from discord import PermissionOverwrite, Guild
from discord.ext import commands
import sqlite3
from random import randint
from discord.utils import get
import json
from os import mkdir, path
import sys


class DiscordGames(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(hidden=True)
	async def game(self, ctx, game_index=None, action="p"):
		if game_index:
			try:
				game_index = int(game_index)
			except:
				await ctx.channel.send("Please input the key index of the game you want to play!")
			else:
				#Checks if the prompted game index exists
				playable_games = {1:"Guess The Number:-:solo"}
				if game_index not in playable_games:
					await ctx.channel.send(f"Sorry, we do not have a game that has an index of {game_index}")
					return
				else:
					users = [ctx.author]
					game_name, mode = playable_games[game_index].split(":-:")
					if game_index == 1:
						from games.lib.GuessTheNumber import GuessTheNumber
						game_library = GuessTheNumber()

				action = action.lower()
				game_commands = ("p", "play", "h", "help", "s", "highscore")
				if action in game_commands:
					if action in game_commands[:2]:
						#Creates a sqlite database for active rooms
						game_folder = "#" + str(ctx.guild.id)
						if not path.exists(f"games/#{ctx.guild.id}"):
							mkdir(f"games/#{ctx.guild.id}")
						guild_game_data = sqlite3.connect(f"games/#{ctx.guild.id}/guild_game_data.db")
						active_rooms = guild_game_data.cursor()
						active_rooms.execute("CREATE TABLE IF NOT EXISTS activerooms(channel_id text, users_id text, roomid text, game text)")
						active_rooms.execute("SELECT users_id FROM activerooms")
						active_rooms_users = active_rooms.fetchall()
						is_user_not_in_game = True
						for list_of_users in active_rooms_users:
							list_of_users = list_of_users[0]
							list_of_users = list_of_users.split("---")
							if str(ctx.author.id) in list_of_users:
								is_user_not_in_game = False
								break

						#Checks if user is not in a game room
						if is_user_not_in_game:

							#Checks if the number of active rooms reach it limit
							active_rooms.execute("SELECT * FROM activerooms")
							num_of_act_rm = len(active_rooms.fetchall())
							if num_of_act_rm <= 30:
								#Creates a Game Category for game rooms(channels)
								permission_overwrites = {ctx.guild.default_role: PermissionOverwrite(read_messages=False), ctx.author: PermissionOverwrite(read_messages=True)}
								if not get(ctx.guild.categories, name="Games"):
									await ctx.guild.create_category("Games", overwrites=permission_overwrites)

								while True:
									#Get's a random number as a unique game room id that ranges from 0 to 273 in base 10 and translates it to base 16
									game_room_id = hex(randint(0,273))[2:]
									#Checks if room_id is already taken
									active_rooms.execute("SELECT roomid FROM activerooms WHERE roomid = '{}'".format(game_room_id))
									all_room_id = active_rooms.fetchall()
									if not all_room_id:
										#Naming a game room
										game_room_name = f"{game_index}-{'-'.join(game_name.lower().split())}-#{game_room_id}"

										#Creates a game room
										game_room_category = get(ctx.guild.categories, name="Games")
										game_room_channel = await ctx.guild.create_text_channel(game_room_name, category=game_room_category, overwrites=permission_overwrites)
										break

								data = (str(game_room_channel.id), str("---".join([str(each_user.id) for each_user in users])), str(game_room_id), str(game_name))
								active_rooms.execute("INSERT INTO activerooms VALUES {}".format(data))

								await ctx.channel.send(f"{ctx.author.mention}, you're now invited to your game channel.")

								#Send the user the rules of the game room
								await game_room_channel.send(f"\nHello {ctx.author.mention}!```\nOnce you enter a game room, you cannot enter another game room again until you leave this game room.\nYou can not invoke any command except game commands in game rooms.```")

								bot_response = game_library.channel_preparation()
								for response in bot_response:
									await game_room_channel.send(response)
							else:
								await ctx.channel.send("Sorry, the number of active game rooms are full!")

						else:
							await ctx.channel.send(f"{ctx.author.mention}, you are still in a game, please finish or quit that game room first.\n\nTo quit, use the command --q in that game room.\n\nWarning: Admins, please do not delete an active game room because it might lead to certain bugs.")

						guild_game_data.commit()
						guild_game_data.close()
					elif action in game_commands[2:4]:
						await ctx.channel.send("Game description")
					elif action in game_commands[4:6]:
						await ctx.channel.send("Game highscores")
				else:
					await ctx.send("```\nChoose the action that you want to do:\t\n(--p) Starts Game\t\n(--h) Shows game description\t\n(--s) Top 10 High Scores```")

		else:
			await ctx.channel.send("list of playable games!")
			#Show list of playable games
			pass


def setup(bot):
	bot.add_cog(DiscordGames(bot))