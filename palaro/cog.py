import discord
from discord.ext import commands

from palaro.services.gtn import GuessTheNumber

class GameConfig(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.available_games = {"guess-the-number":GuessTheNumber}

	#=========================HIDDEN COMMANDS, SHOULD NOT BE ACCESSIBLE FOR USERS=========================
	@commands.command(hidden=True)
	async def response_awaiter(self, func, recipient, author_mention):
		bot_response, instant_response = func

		for each_response in bot_response:
			await recipient.send(f"{author_mention}```\n{each_response}```")

		for each_response in instant_response:
			try:
				await each_response
			except discord.Forbidden:
				pass

	@commands.command(hidden=True)
	async def analyze_user_response(self, message, command_prefix):
		#==============================Checks the message if it is a command or not==============================
		if message.content.split()[0][0] == command_prefix:
			#==============================Checks which command is being invoked==============================
			if message.content.split()[0][1:] in [each_command.name for each_command in self.bot.commands if each_command.cog_name == "GameConfig"]:
				#==============================Commands under Game Configs can only be invoked in game channels==============================
				if message.channel.category.name.title() == "Palaro" and message.channel.name in self.available_games:
					invoker = message.content.split()[0][1:]
					if invoker == "play":
						await self.play(self, message)
					elif invoker == "rules":
						await self.rules(self, message)
					elif invoker == "quit":
						await self.quit(self, message)
				else:
					await message.channel.send(f"{message.author.mention}```\nThis command is only available at game channels.```")
			else:
				#==============================Commands not under Game Configs can be invoked everywhere except game channels==============================
				if message.channel.category.name == "Palaro" and message.channel.name in self.available_games:
					await message.channel.purge(limit=1)
					await message.channel.send(f"{message.author.mention}```\nOnly game commands can be invoked here.```")
				else:
					await self.bot.process_commands(message)
		#==============================If message is not a command, checks if it is sent in game channels==============================
		elif message.channel.category.name.title() == "Palaro" and message.channel.name in self.available_games:
			await self.response_awaiter(self, self.available_games[message.channel.name](message).user_response(message), message.channel, message.author.mention)

	#=========================EVERY GAME SHOULD HAVE THE FOLLOWING FUNCTIONS=========================
	@commands.command()
	async def play(self, message):
		await self.response_awaiter(self, self.available_games[message.channel.name](message).start(message), message.channel, message.author.mention)

	@commands.command()
	async def rules(self, message):
		await self.response_awaiter(self, self.available_games[message.channel.name](message).help(message), message.channel, message.author.mention)

	@commands.command()
	async def quit(self, message):
		await self.response_awaiter(self, self.available_games[message.channel.name](message).terminate(message), message.channel, message.author.mention)

def setup(bot):
	bot.add_cog(GameConfig(bot))