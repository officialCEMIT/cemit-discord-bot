import discord
from discord.ext import commands
from discord.utils import get


class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def poll(self, ctx):
        emoji_box = list("🟥🟧🟨🟩🟪🔴🟠🟡🟢🟣")

        message_body = ""  # stores the choices as a message
        choices = ctx.message.content[6:].strip().split(',')  # gets the choices from the csv
        if len(choices) <= 10:  # checks if the choices is within the limit
            for i in range(len(choices)):  # builds the message body
                message_body += f"{emoji_box[i]}:  {choices[i]} \n" 
            msg = await ctx.message.channel.send(message_body) # sends the message body and store it to a variable
            for i in range(len(choices)):
                await msg.add_reaction(emoji_box[i]) # add the reaction to the message for voting
        else:  # Sends alternate message if it is over the limit
            await ctx.message.channel.send("The limit is 10 choices only. Please try again.")


def setup(bot):
    bot.add_cog(Poll(bot))
