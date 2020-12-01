from peewee import *
from main import db

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
	db.create_tables([GuessTheNumber])