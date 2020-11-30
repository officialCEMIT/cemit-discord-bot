"""
    This command will allow a user to type a question onto discord chat and return the most relevant link from Stack Overflow.
"""

import discord
from discord.ext import commands
from discord.utils import get

from utils.core.api import CEMIT

from stackapi import StackAPI

cemit = CEMIT()

class SOQuestionFinder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def so(self, ctx, *, question):
        try:
            site = StackAPI("stackoverflow")                                            #Search in Stack Overflow
            questions = site.fetch("search", sort = "relevance", intitle = question)    #Fetch questions according to relevance to search query
            questions_list = questions["items"]                                         #Assign fetched questions to a variable
            top_question = questions_list[0]                                            #Get latest question
            await ctx.send(top_question["link"])                                        #Print the link to the question
        except IndexError:
            await ctx.send("No question matched your search query. Try again")          #Print error message if no questions matched search query

def setup(bot):
    bot.add_cog(SOQuestionFinder(bot))