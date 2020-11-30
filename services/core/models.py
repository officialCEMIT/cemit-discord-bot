from peewee import *
from main import db

# TODO: UserDB

class ChannelPoint(Model):
    # TODO: USER DB
    # user = ForeignKeyField()
    points = IntegerField()

    class Meta:
        database = db


def setup():
    db.create_tables([ChannelPoint])