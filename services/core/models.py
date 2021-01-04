from peewee import *
from main import db


class UserDatabase(Model):
    # TODO: USER DB
    # user = ForeignKeyField()

	#For User Main Data
    username = TextField()
    user_id = TextField()
    nickname = TextField()
    #first_name = TextField()
    #last_name = TextField()
    validation_date = DateField()

    class Meta:
        database = db


def setup():
    db.create_tables([UserDatabase])