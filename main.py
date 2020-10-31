import discord 
from decouple import config
from utils.client import bot

def main():
    token = config('BOT_TOKEN')
    bot.run(token)

if __name__ == "__main__":
    # CLICKUP DEMO
    # TEST
    main()