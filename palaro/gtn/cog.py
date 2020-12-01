from peewee import *
from os.path import exists
from random import randint
from math import cos, log
from main import db
from palaro.gtn.models import setup as gtn_models, GuessTheNumber

class GuessTheNumber:
	def __init__(self, message):
		self.rules = (
					"Welcome to Guess The Number.",
					"Goal: Guess what number am I thinking.",
					"To play:\n\tEasy:\t'play' or 'play e'\n\tHard:\t'play h'\n\tInsane:\t'play i'",
					"To quit:\n\t'quit'",
					"Rules:\n\tThe purpose of this channel is to entertain every player.\n\tAll commands invoked in here except game commands are prohibited.\n\tRespect each player.",
					)

	def user_response(self, message):
		result, instant_result = [], []

		#=========================Connecting to Database=========================
		db.connect()
		gtn_models()

		#=========================Fetching User's Data=========================
		player_id = int(message.author.id)
		try:
			player_data = GuessTheNumber.get(GuessTheNumber.player_id == player_id)
		except:
			player_data = None

		#=========================Checking the message if it is a guess or a command=========================
		try:
			user_guess = int(message.content)
		except:
			#=========================Message is not a guess=========================
			command_invoked = message.content.split()
			action = command_invoked[0]

			if action == 'play':
				#=========================Checking if player is still in game=========================
				if not player_data:
					#=========================Setting up the values=========================
					try:
						difficulty = command_invoked[1].lower()
						if difficulty not in ("e", "h", "i"):
							result = ("Please specify what difficulty do you want to play:\n\n\tEasy:\t'play e'\n\tHard:\t'play h'\n\tInsane:\t'play i'",)
					except IndexError:
						difficulty = "e"

					secret_number, range_low_number, range_high_number = self.get_number(difficulty)
					guesses = 0

					#=========================Saving to Database=========================
					player_data = GuessTheNumber(
								player_id=player_id,
								secret_number=secret_number,
								range_low_number=range_low_number,
								range_high_number=range_high_number,
								difficulty=difficulty,
								guesses=guesses
								)

					player_data.save()

					result = (f"You are now playing Random Number in {[['Insane', 'Hard'][difficulty == 'h'], 'Easy'][difficulty == 'e']} Mode.\n\nGuess the random number which is in between ({range_low_number}, {range_high_number}), both included.",)
				else:
					result = ("Please finish your current game first or quit it.\n\nTo quit:\t'quit'",)
			elif action == 'quit':
				if not player_data:
					result = ("You are not in a game, yet.\nTo play:\n\tEasy:\t'play' or 'play e'\n\tHard:\t'play h'\n\tInsane:\t'play i'",)
				else:
					player_data.delete_instance()
					result = ("Game terminated, you can now play another game.",)
			elif action == "rules":
				result = self.rules
			else:
				instant_result = (message.channel.purge(limit=1), message.author.send(f"```\nOnly game commands or guesses are allowed to be sent in {message.channel.name}.```"))
		else:
			#=========================Message is a guess=========================
			if player_data:
				#=========================Player has data=========================
				player_data.guesses += 1

				if user_guess == player_data.secret_number:
					score = self.pointing_system(player_data.guesses, player_data.range_low_number, player_data.range_high_number)
					result = (f"Congratulations!\nYou got it in {player_data.guesses} {['guess', 'guesses'][player_data.guesses == 1]}!\nAcquired: {score} Channel Points","Do you want to play again?\nTo play:\n\tEasy:\t'play' or 'play e'\n\tHard:\t'play h'\n\tInsane:\t'play i'")
					player_data.delete_instance()
				else:
					number_range = (player_data.range_low_number, player_data.range_high_number)
					result = (f"Sorry, your answer is wrong. Your answer is {['lower', 'higher'][user_guess > player_data.secret_number]} than the hidden number.\nMode: {[['Insane', 'Hard'][player_data.difficulty == 'h'], 'Easy'][player_data.difficulty == 'e']}\nRange: {number_range} both included\nGuesses: {player_data.guesses}",)
					player_data.save()
			else:
				#=========================Player has no data=========================
				instant_result = (message.channel.purge(limit=1),)
				result = ("You are not in a game, yet.\nTo play:\n\tEasy:\t'play' or 'play e'\n\tHard:\t'play h'\n\tInsane:\t'play i'",)

		#=========================Closing The Database=========================
		db.close()

		return result, instant_result

	def get_number(self, difficulty):
		if difficulty == "e":
			range_low_number, range_high_number = (0,100)
		elif difficulty == "h":
			range_low_number, range_high_number = (-50,250)
		elif difficulty == "i":
			range_low_number, range_high_number = (-500,500)

		return randint(range_low_number, range_high_number + 1), range_low_number, range_high_number

	def pointing_system(self, guesses, range_low_number, range_high_number):
		total_range = range_high_number - range_low_number + 1
		return int((((total_range / 2) * (1 / cos((guesses / 10) - 1)) - (total_range / 2)) * (log(total_range) + 1 - guesses)) / log(total_range))