import discord
from discord.ext import commands
from discord.utils import get

from client import CHANNEL_MAP

from utils.core.api import CEMIT
from utils.core.errors import MemberExists, MemberNotFound

cemit = CEMIT()

class Membership(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def validate(self, ctx, user_id):
        member = f"<@{ctx.author.id}>"
        
        if ctx.channel.name == CHANNEL_MAP['valid'] or ctx.channel.name == CHANNEL_MAP['bot']:
            """
            TODO: 
                - Check id in DB
                - Check if already validated
            """
            try:
                user = cemit.validate_member(user_id, ctx.author.name)
                role = get(ctx.author.guild.roles, name='MEMBER')

                b = user.get("batch")
                if (batch := get(ctx.author.guild.roles, name=b)):
                    pass 
                else:
                    batch = await ctx.author.guild.create_role(name=b)
                await ctx.author.add_roles(role, batch)
                await ctx.author.remove_roles(get(ctx.author.guild.roles, name='UNVALIDATED'))

                user_info = user['information']
                first_name = user_info.get("first_name")
                last_name = user_info.get("last_name")

                embed = discord.Embed(
                    title = f"Thanks for validating! {first_name} {last_name}",
                    color=0x2ecc71,
                    description="You can now access our exclusive channels for members!"
                )
                embed.set_thumbnail(url=ctx.author.avatar_url)
                await ctx.channel.send(embed=embed)
            except MemberExists:
                await ctx.channel.send(f"Hey! {member} The CEMIT member ID you sent is already validated")
                await ctx.channel.send("If you think this is a mistake, @ an online officer to assist you")
            except MemberNotFound:
                await ctx.channel.send(f"Sorry {member}, The ID you sent does not match any of the CEMIT members regstered")
                await ctx.channel.send("If you think this is a mistake, @ an online officer to assist you")
            except Exception as e:
                bot_channel = get(self.bot.get_all_channels(), name=CHANNEL_MAP['bot'])
                await bot_channel.send(f"ERROR: {e}")
                await ctx.channel.send(f"Oops! Something went wrong, try again later.")

def setup(bot):
    bot.add_cog(Membership(bot))