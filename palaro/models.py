from peewee import *
from main import db

class PlayerGameDatabase(Model):
    #For User as a player
    user_id = TextField()
    overall_points = IntegerField()
    coins = IntegerField()
    bag = TextField()
    bank = IntegerField()

    #For Channel Points
    channel_points = IntegerField()
    channel_message_sent = TextField()

    class Meta:
        database = db

class GuessTheNumber(Model):
	player_id = IntegerField()
	secret_number = IntegerField()
	range_low_number = IntegerField()
	range_high_number = IntegerField()
	difficulty = CharField()
	guesses = IntegerField()

	class Meta:
		database = db


def setup():
	db.create_tables([PlayerGameDatabase, GuessTheNumber])