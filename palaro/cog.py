import discord
from discord.ext import commands

from palaro.services.gtn import GuessTheNumber

from main import db
from palaro.models import PlayerGameDatabase as PLAYERDB

from math import log, exp as euler_exponent, e as euler_num

class GameConfig(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.available_games = {"guess-the-number":GuessTheNumber}

	#=========================HIDDEN COMMANDS, SHOULD NOT BE ACCESSIBLE FOR USERS=========================

	async def fetch_user_data(self, fetched_user_id):
		try:
			user_data = PLAYERDB.get(PLAYERDB.user_id == str(fetched_user_id))
		except:
			user_data = None

		return user_data

	#Pseudo User Validation
	async def player_validation(self, message):
		user_data = await self.fetch_user_data(message.author.id)

		#=========================Saving to Database=========================
		if not user_data:
			user_data = PLAYERDB(
							#For User as a player
							user_id = message.author.id,
							overall_points = 0,
							coins = 0,
							bag = "",
							bank = 0,

							#For Channel Points
							channel_points = 0,
							channel_message_sent = ""
						)

			user_data.save()

		db.close()

		return user_data

	async def string_from_to_dict(self, from_or_to, var_value, separator=("", ""), returned_as_tuple=False):
		if from_or_to == "to":
			if var_value == "":
				if returned_as_tuple:
					return (("", 0), )
				else:
					return {}
			else:
				splitted_message = var_value.split(separator[0])
				try:
					list_message = [tuple(each_pair.split(separator[1])) for each_pair in splitted_message]
				except:
					list_message = [tuple(each_pair.split(separator[0])) for each_pair in splitted_message]
				if returned_as_tuple:
					return tuple(list_message)

				dict_message = {}
				for key, value in list_message:
					dict_message[key] = int(value)

				return dict_message

		elif from_or_to == "from":
			try:
				list_message = [f"{each_key}{separator[1]}{str(var_value[each_key])}" for each_key in var_value]
			except:
				list_message = [f"{each_key}{separator[0]}{str(var_value[each_key])}" for each_key in var_value]
			string_message = separator[0].join(list_message)

			return string_message

	async def coins_management(self, message, add_coins, add_points, source):
		'''
			channel_message_sent is the amount of messages sent by a user in each channel that is in string form.
			This variable should be in dictionary variable but there is no dictionary field in peewee's SqliteDatabase.

			Structure:
				Each key and value is separated by ':___:'
				Example:
					channel-one:___:27

				Each pair is separated by ',|-|, '
				Example:
					channel-one:___:27,|-|,  channel-three:___:96
		'''

		user_data = await self.fetch_user_data(message.author.id)

		if source == "channel":
			user_data.channel_points += add_points

			#Change Value of channel message sent
			#Convert String to Dict
			dict_channel_message = await self.string_from_to_dict("to", user_data.channel_message_sent, (",|-|, ", ":___:"))
			try:
				dict_channel_message[message.channel.name] += 1
			except:
				dict_channel_message[message.channel.name] = 1
			#Convert Dict to String
			string_channel_message = await self.string_from_to_dict("from", dict_channel_message, (",|-|, ", ":___:"))

			user_data.channel_message_sent = string_channel_message

		elif source == "game":
			user_data.coins += add_coins
			user_data.overall_points += add_points

		user_data.save()

	async def response_awaiter(self, func, recipient, author_mention):
		bot_response, instant_response = func

		for each_response in bot_response:
			await recipient.send(f"{author_mention}```\n{each_response}```")

		for each_response in instant_response:
			try:
				await each_response
			except discord.Forbidden:
				pass

	async def analyze_user_response(self, message, command_prefix):
		#==============================Channel Points==============================
		#For every message sent by a user, add a point to a player (Message should be sent at al channels except at game channels)
		if not await self.player_validation(message):
			#This outcome have zero percent chance to come out yet because cemit legitimate validation systerm is not yet working
			await ctx.channel.send("Sorry, but you are not validated as a member, yet!")
			return

		message_length = len(message.content)

		#==============================Checks the message if it is a command or not==============================
		if message.content.split()[0][0] == command_prefix:
			unique_cog_commands = ("coins", "channelpoints")

			#==============================Checks which command is being invoked==============================
			if message.content.split()[0][1:] in [each_command.name for each_command in self.bot.commands if each_command.cog_name == "GameConfig"]:
				invoker = message.content.split()[0][1:]
				#==============================Commands under Game Configs can only be invoked in game channels except thios commands==============================
				if invoker in unique_cog_commands:
					if invoker == "coins":
						await self.coins(self, message)
					elif invoker == "channelpoints":
						await self.channelpoints(self, message)
				#==============================Commands under Game Configs can only be invoked in game channels except commands above==============================
				if message.channel.category.name.title() == "Palaro" and message.channel.name in self.available_games:
					if invoker == "play":
						await self.play(self, message)
					elif invoker == "rules":
						await self.rules(self, message)
					elif invoker == "quit":
						await self.quit(self, message)
					elif invoker not in unique_cog_commands:
						await message.channel.purge(limit=1)

				elif invoker not in unique_cog_commands:
					await message.channel.send(f"{message.author.mention}```\nThis command is only available at game channels.```")
			else:
				#==============================Commands not under Game Configs can be invoked everywhere except game channels==============================
				if message.channel.category.name == "Palaro" and message.channel.name in self.available_games:
					await message.channel.purge(limit=1)
				else:
					await self.bot.process_commands(message)
		#==============================If message is not a command, checks if it is sent in game channels==============================
		else:
			if message.channel.category.name.title() == "Palaro" and message.channel.name in self.available_games:
				result, instant_result, final_coins_points = self.available_games[message.channel.name](message).user_response(message)
				await self.response_awaiter((result, instant_result), message.channel, message.author.mention)

				if final_coins_points[0]:
					await self.coins_management(message, final_coins_points[1], final_coins_points[2], "game")
			else:
				#==============================Channel points can only be gathered on non-game channels and non-commands messages==============================
				await self.coins_management(message, message_length, message_length, "channel")


	#=========================EVERY GAME SHOULD HAVE THE FOLLOWING FUNCTIONS=========================
	@commands.command()
	async def play(self, message):
		await self.response_awaiter(self.available_games[message.channel.name](message).start(message), message.channel, message.author.mention)

	@commands.command()
	async def rules(self, message):
		await self.response_awaiter(self.available_games[message.channel.name](message).help(message), message.channel, message.author.mention)

	@commands.command()
	async def quit(self, message):
		await self.response_awaiter(self.available_games[message.channel.name](message).terminate(message), message.channel, message.author.mention)


	#=========================COG'S UNIQUE COMMANDS=========================
	@commands.command()
	async def coins(self, message):
		#Shows the player, how many coins does he/she has
		user_data = await self.fetch_user_data(message.author.id)
		if user_data:
			await message.channel.send(f"```\nCoins:\t{user_data.coins}```")
		else:
			await message.channel.send(f"```\nCoins:\t0```")

	@commands.command()
	async def channelpoints(self, message):
		#Shows the player, how many channel points does he/she has
		user_data = await self.fetch_user_data(message.author.id)
		if user_data:
			#Convert String to Tuple
			tuple_channel_message = await self.string_from_to_dict("to", user_data.channel_message_sent, (",|-|, ", ":___:"), True)
			string_count = ""
			try:
				for channel_key, message_sents in tuple_channel_message:
					string_count += f"\t{channel_key}:\t{message_sents}\n"
			except ValueError:
				string_count += "\n"
			await message.channel.send(f"```\nChannel Points:\t{user_data.channel_points}\n\nChannel Message Count:\n{string_count}```")
		else:
			await message.channel.send(f"```\nChannel Points:\t0\n\nChannel Message Count:\n\tNone```")



def setup(bot):
	bot.add_cog(GameConfig(bot))