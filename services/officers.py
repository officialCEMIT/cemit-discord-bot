import discord
from discord.ext import commands
from discord.utils import get

class Officers(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	@commands.has_role("OFFICERS")
	async def announce(self, ctx, *, message):
		#Channel checker
		def channel_check(ctx, channel_name_id):
			if channel_name_id[:2] == "--":
				return get(ctx.guild.channels, name=channel_name_id[2:])
			elif channel_name_id[:2] == "<#" and channel_name_id[-1] == ">":
				return ctx.guild.get_channel(int(channel_name_id[2:-1]))
			else:
				return None

		#Recipients - Message Separator
		recipient_with_message = message.split()
		recipient_channels = []
		prepared_message = ""
		for each_channel in recipient_with_message:
			#If word has "--" prefix or has "<@!" as prefix and ">" as suffix, this means that it might be a channel
			if each_channel[:2] == "--" or (each_channel[:2] == "<#" and each_channel[-1] == ">"):
				#Checks if the name(word excluded the "--" prefix) or id(word excluded the "<@!" as prefix and ">" as suffix) is true
				found_channel = channel_check(ctx, channel_name_id=each_channel)
				if found_channel:
					recipient_channels.append(found_channel)
				else:
					#Text changes depends in what is the prefix of the non-existent name or channel
					await ctx.channel.send(str([each_channel[2:-1] + " id", each_channel[2:]][each_channel[:2] == "--"]) + f" is not a channel in this server!")
					print(f"A user tried to announce to a non-existent channel in {ctx.guild.name}!")
			else:
				#Separates the message from the recipient channels
				prepared_message = recipient_with_message[recipient_with_message.index(each_channel):]
				#Stops the iteration because this word is now the first word of the message
				break

		#Checks if there are any channels collected
		if len(recipient_channels) == 0:
			await ctx.channel.send(f"Please input at least one channel!")
			print(f"An announcement has no recipient!")
			return

		#Checks if announcement has message
		if prepared_message == "":
			await ctx.channel.send(f"Announcement has no message!")
			print(f"An announcement has no message!")
			return
		else:
			prepared_message = " ".join(prepared_message)

		#Sends the announcement for each channel
		for each_channel in recipient_channels:
			await each_channel.send(f"{prepared_message}")
			print(f"An announcement has been sent by {ctx.message.author}!")


def setup(bot):
	bot.add_cog(Officers(bot))