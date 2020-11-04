import discord
from discord.ext import commands
from discord.utils import get


class Admin(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	#Kick command
	@commands.command()
	async def kick(self, ctx, member : discord.Member, *, reason=None):
		if ctx.message.author.top_role.permissions.administrator:
			await member.kick(reason=reason)
			await ctx.channel.send(f"Kicked {member.mention}\nReason: {reason}")
		else:
			await ctx.channel.send(f"Only admins can kick members!")

	#Ban command
	@commands.command()
	async def ban(self, ctx, member : discord.Member, *, reason=None):
		if ctx.message.author.top_role.permissions.administrator:
			await member.ban(reason=reason)
			await ctx.channel.send(f"Banned {member.mention}\nReason: {reason}")
		else:
			await ctx.channel.send(f"Only admins can ban members!")

	#Unban command
	@commands.command()
	async def unban(self, ctx, *, member):
		if ctx.message.author.top_role.permissions.administrator:
			banned_list = await ctx.guild.bans()

			if len(banned_list) != 0:
				for banned_member in banned_list:
					user = banned_member.user

					if (user.name + "#" + user.discriminator) == member:
						await ctx.guild.unban(user)
						await ctx.channel.send(f"Unbanned {user.mention}")
						return
			else:
				await ctx.channel.send(f"Nothing to unban!")

		else:
			await ctx.channel.send(f"Only admins can unban members!")

	#Show list of banned members
	@commands.command()
	async def banlist(self, ctx):
		if ctx.message.author.top_role.permissions.administrator:
			banned_list = await ctx.guild.bans()

			if len(banned_list) != 0:
				return_list = ""
				for banned_member in banned_list:
					user = banned_member.user
					return_list += f"\n{user.name}#{user.discriminator}"

				await ctx.channel.send(f"Banned Members:{return_list}")
			else:
				await ctx.channel.send(f"No Banned Members!")
		else:
			await ctx.channel.send(f"Only admins can see banned members!")

	#Purge command
	@commands.command()
	async def clear(self, ctx, amount=0):
		if ctx.message.author.top_role.permissions.administrator:
			if amount >= 0:
				amount += 1
				await ctx.channel.purge(limit=amount)

def setup(bot):
	bot.add_cog(Admin(bot))