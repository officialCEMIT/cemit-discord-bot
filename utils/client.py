from discord import Client, Intents
from discord.utils import get

from .core.api import CEMIT
from .core.errors import MemberExists, MemberNotFound

intents = Intents.default()
intents.members = True
bot = Client(intents=intents)

cemit = CEMIT()

CHANNEL_MAP = {
    'bot': '🤖cemit-discord-bot',
    'valid': 'validation✅'
}

@bot.event
async def on_message(message):
    if message.content[:2] == '!!' and not message.author.bot:
        q = message.content[2:].split(" ")

        if q[0] == 'validate' and message.channel.name == CHANNEL_MAP['valid'] and len(q) > 1:
            if (user_id := q[1]):
                """
                TODO: 
                    - Check id in DB
                    - Check if already validated
                """

                try:
                    cemit.validate_member(user_id)
                    role = get(message.author.guild.roles, name='MEMBER')
                    await message.author.add_roles(role)
                    await message.channel.send("Successfully Validated")
                except MemberExists:
                    await message.channel.send("The CEMIT member ID you sent is already exists here")
                    await message.channel.send("If you think this is a mistake, @ an online officer to assist you")
                except MemberNotFound:
                    await message.channel.send("The ID you sent does not match any of the CEMIT members registered")
                    await message.channel.send("If you think this is a mistake, @ an online officer to assist you")

@bot.event
async def on_ready():
    print(f"DISCORD {bot.user.name}(BOT) Ready!")

    # TODO: SEARCH FOR THE BOT CHANNEL EFFICIENTLY 
    bot_channel = get(bot.get_all_channels(), name=CHANNEL_MAP['bot'])
    await bot_channel.send("I'm online!")

@bot.event
async def on_member_join(member):
    role = get(member.guild.roles, name='UNVALIDATED')
    await member.add_roles(role)