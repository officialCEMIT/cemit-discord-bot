from peewee import *
from os.path import exists
from random import randint
from math import cos, log
from main import db
from palaro.models import GuessTheNumber as GTNMODEL

class GuessTheNumber:
	def __init__(self, message_or_ctx):
		self.result, self.instant_result = [], []
		self.game_channel = "guess-the-number"
		self.rules = ("Welcome to GUESS THE NUMBER.\nGoal: Guess what number am I thinking.\nTo play:\n\tEasy:\t'play' or 'play e'\n\tHard:\t'play h'\n\tInsane:\t'play i'\nTo quit:\n\t'quit'\nRules:\n\tThe purpose of this channel is to entertain every player.\n\tAll commands invoked in here except game commands are prohibited.\n\tRespect each player.",)
		#=========================Fetching User's Data=========================
		self.fetched_player_id = int(message_or_ctx.author.id)

		try:
			self.player_data = GTNMODEL.get(GTNMODEL.player_id == self.fetched_player_id)
		except:
			self.player_data = None


	#=========================THIS GAME'S UNIQUE FUNCTIONS=========================
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
		

	#=========================EVERY GAME SHOULD HAVE THE FOLLOWING FUNCTIONS=========================
	def user_response(self, message):
		#Tells if the returned value is the finals points of the player
		final_coins_points = (False, 0)
		#=========================Checking the message if it is a guess or a command=========================
		try:
			user_guess = int(message.content)
		except:
			self.instant_result = (message.channel.purge(limit=1), message.author.send(f"```\nOnly game commands or guesses are allowed to be sent in {message.channel.name}.```"))
		else:
			#=========================Message is a guess=========================
			if self.player_data:
				#=========================Player has data=========================
				self.player_data.guesses += 1

				if user_guess == self.player_data.secret_number:
					score = self.pointing_system(self.player_data.guesses, self.player_data.range_low_number, self.player_data.range_high_number)
					self.result = (f"Congratulations!\nYou got it in {self.player_data.guesses} {['guess', 'guesses'][self.player_data.guesses == 1]}!\nAcquired: {score} Channel Points","Do you want to play again?\nTo play:\n\tEasy:\t'play' or 'play e'\n\tHard:\t'play h'\n\tInsane:\t'play i'")
					self.player_data.delete_instance()
					final_coins_points = (True, int(score), int(score))
				else:
					number_range = (self.player_data.range_low_number, self.player_data.range_high_number)
					self.result = (f"Sorry, your answer is wrong. Your answer is {['lower', 'higher'][user_guess > self.player_data.secret_number]} than the hidden number.\nMode: {[['Insane', 'Hard'][self.player_data.difficulty == 'h'], 'Easy'][self.player_data.difficulty == 'e']}\nRange: {number_range} both included\nGuesses: {self.player_data.guesses}",)
					self.player_data.save()
			else:
				#=========================Player has no data=========================
				self.instant_result = (message.channel.purge(limit=1),)
				self.result = ("You are not in a game, yet.\nTo play:\n\tEasy:\t'play' or 'play e'\n\tHard:\t'play h'\n\tInsane:\t'play i'",)

		#=========================Closing The Database=========================
		db.close()

		return self.result, self.instant_result, final_coins_points

	def start(self, message):
		#=========================Checking if player is still in game=========================
		if not self.player_data:
			#=========================Setting up the values=========================
			try:
				difficulty = message.content.split()[1].lower()
				if difficulty not in ("e", "h", "i"):
					self.result = ("Please specify what difficulty do you want to play:\n\n\tEasy:\t'play e'\n\tHard:\t'play h'\n\tInsane:\t'play i'",)
			except IndexError:
				difficulty = "e"

			secret_number, range_low_number, range_high_number = self.get_number(difficulty)
			print(secret_number)
			guesses = 0

			#=========================Saving to Database=========================
			self.player_data = GTNMODEL(
						player_id = self.fetched_player_id,
						secret_number=secret_number,
						range_low_number=range_low_number,
						range_high_number=range_high_number,
						difficulty=difficulty,
						guesses=guesses
						)

			self.player_data.save()

			self.result = (f"You are now playing Random Number in {[['Insane', 'Hard'][difficulty == 'h'], 'Easy'][difficulty == 'e']} Mode.\n\nGuess the random number which is in between ({range_low_number}, {range_high_number}), both included.",)
		else:
			self.result = ("Please finish your current game first or quit it.\n\nTo quit:\t'quit'",)
		return self.result, self.instant_result

	def help(self, message):
		self.result = self.rules
		return self.result, self.instant_result

	def terminate(self, message):
		if not self.player_data:
			self.result = ("You are not in a game, yet.\nTo play:\n\tEasy:\t'play' or 'play e'\n\tHard:\t'play h'\n\tInsane:\t'play i'",)
		else:
			self.player_data.delete_instance()
			self.result = ("Game terminated, you can now play another game.",)
		return self.result, self.instant_result