import discord, pkgutil
from peewee import SqliteDatabase
from decouple import config
from client import bot


db = SqliteDatabase('cemit.db')

def startup():
    db.connect()    

    from services.core.models import setup as core_models
    from palaro.models import setup as game_models
    #TODO: AUTOMATIC TABLE DETECTION
    #TODO: Migrations
    core_models()
    game_models()
    
    db.close()

if __name__ == "__main__":
    startup()
    token = config('BOT_TOKEN')
    
    bot.load_extension("services.membership")
    bot.load_extension("services.stackoverflow")
    bot.load_extension("services.admin")
    bot.load_extension("services.officers")
    bot.load_extension("services.poll")

    #PALARO
    bot.load_extension("palaro.cog")
    bot.run(token)