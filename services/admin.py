import discord
from discord.ext import commands

#I print the outputs for troubleshooting
class Admin(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	#Kick command
	@commands.command()
	async def kick(self, ctx, member : discord.Member, *, reason=None):
		#Checks if user has the top role/admin
		if ctx.message.author.top_role.permissions.administrator:
			await member.kick(reason=reason)
			await ctx.channel.send(f"Kicked {member.mention}\n\tReason: {reason}")
			print(f"Kicked {member}\n\tReason: {reason}!")
		else:
			await ctx.channel.send(f"Only admins can kick members!")
			print(f"A member tried to kick another member!")

	#Ban command
	@commands.command()
	async def ban(self, ctx, member : discord.Member, *, reason=None):
		#Checks if user has the top role/admin
		if ctx.message.author.top_role.permissions.administrator:
			await member.ban(reason=reason)
			await ctx.channel.send(f"Banned {member.mention}\n\tReason: {reason}")
			print(f"Banned {member}\n\tReason: {reason}!")
		else:
			await ctx.channel.send(f"Only admins can ban members!")
			print(f"A member tried to ban another member!")

	#Unban command
	@commands.command()
	async def unban(self, ctx, *, member):
		#Checks if user has the top role/admin
		if ctx.message.author.top_role.permissions.administrator:
			banned_list = await ctx.guild.bans()

			#Checks if there are banned users
			if len(banned_list) != 0:
				#Checks if the given name of member is in correct format
				if "#" not in member:
					await ctx.channel.send("Member name not in correct format. Should be in name#discriminator format!")
					print(f"Member name format incorrect!")
				#Checks if the user is in the list of banned members
				for banned_member in banned_list:
					user = banned_member.user

					if (user.name + "#" + user.discriminator) == member:
						await ctx.guild.unban(user)
						await ctx.channel.send(f"Unbanned {user.mention}")
						print(f"Unbanned {user}!")
						return
			else:
				await ctx.channel.send(f"Nothing to unban!")
				print(f"Banned list is empty!")

		else:
			await ctx.channel.send(f"Only admins can unban members!")
			print(f"A member tried to unban a member!")

	#Show list of banned members
	@commands.command()
	async def banlist(self, ctx):
		#Checks if user has the top role/admin
		if ctx.message.author.top_role.permissions.administrator:
			banned_list = await ctx.guild.bans()

			if len(banned_list) != 0:
				return_list = ""
				for banned_member in banned_list:
					user = banned_member.user
					return_list += f"\n{user.name}#{user.discriminator}"

				await ctx.channel.send(f"Banned Members:{return_list}")
				print(f"Banned Members:{return_list}")
			else:
				await ctx.channel.send(f"No Banned Members!")
				print(f"Banned List is empty!")
		else:
			await ctx.channel.send(f"Only admins can see banned members!")
			print(f"A member tried to see the ban list!")

	#Purge command
	@commands.command()
	async def clear(self, ctx, amount=0):
		#Checks if user has the top role/admin
		if ctx.message.author.top_role.permissions.administrator and amount >= 0:
			amount += 1
			await ctx.channel.purge(limit=amount)
			if amount == 2:
				print(f"{amount} message has been cleared in {ctx.channel}")
			elif amount > 2:
				print(f"{amount} messages have been cleared in {ctx.channel}")
		else:
			await ctx.channel.purge(limit=1)


def setup(bot):
	bot.add_cog(Admin(bot))