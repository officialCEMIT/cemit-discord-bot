import discord
from discord.ext import commands
from discord.utils import get

from client import CHANNEL_MAP


class Palaro(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def buy(self, ctx):
        print("TEST")

def setup(bot):
    bot.add_cog(Palaro(bot))