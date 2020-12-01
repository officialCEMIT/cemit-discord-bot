import discord, pkgutil
from peewee import SqliteDatabase
from decouple import config
from client import bot


db = SqliteDatabase('cemit.db')

def startup():
    db.connect()    

    from services.core.models import setup as core_models
    #TODO: AUTOMATIC TABLE DETECTION
    #TODO: Migrations
    core_models()

if __name__ == "__main__":
    startup()
    token = config('BOT_TOKEN')
    
    bot.load_extension("services.membership")
    bot.load_extension("services.stackoverflow")
    bot.load_extension("services.admin")
    bot.load_extension("services.officers")
    bot.load_extension("services.poll")
    bot.load_extension("services.games.games")
    bot.run(token)