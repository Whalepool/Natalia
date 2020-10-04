#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import imp
import os
from functools import partial

# Loading Yaml configuration files 
import yaml

# Mongodb 
from pymongo import MongoClient

# Printing / Outputting
from pprint import pprint 

# Utilities
from utils.str import Str, log
from utils.errors import Errors
from utils.pluginloader import PluginLoader
from utils.rooms import Rooms

# Python telegram bot
import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler


class Natalia( PluginLoader, Errors, Rooms ): 

	
	# Global variables
	PATH = os.path.dirname(os.path.abspath(__file__))
	log.title('Running Natlia in '+PATH)


	# Load config
	config_file = PATH+'/test2.yaml'
	# config_file = PATH+'/test2.sample.yaml'
	log.heading('Loading config '+config_file)
	with open(config_file) as fp:
		config = yaml.load(fp)



	# Start telegram bot
	log.heading('Starting telegram bot')

	# TEST BOT
	# bot = telegram.Bot(token='345427283:AAH1JyTdAMWFc16zlCd62l7mMZPqcjxs1Xw')

	# NATALIA 
	bot = telegram.Bot(token=config['bot_token'])

	updater = Updater(bot=bot,workers=10)
	dp      = updater.dispatcher

	# Mongodb 
	log.heading('Connecting to mongo')
	client  = MongoClient('mongodb://localhost:27017')
	db = client.natalia_tg_bot


	# Bot error handler
	def error(self, bot, update, error):
	    log.print('Update "%s" caused error "%s"' % (update, error))



	# Resolve message data to a readable name 	 		
	def get_name(self, update):

		#pprint(update.message.from_user.username)

		try:
			name = update.message.from_user.username

			# pprint('1')
			# pprint(name)
			# pprint(type(name))

			if (name == 'None') or (name == None):
				name = update.message.from_user.first_name

				# pprint('2')
				# pprint(name)
				# pprint(type(name))

		except (NameError, AttributeError):
			try:
				name = update.message.from_user.first_name

				# pprint('3')
				# pprint(name)
				# pprint(type(name))

			except (NameError, AttributeError):
				name = "no name"



		# pprint('4')
		#pprint(name)
		# pprint(type(name))
			
		return name



	def __init__(self):	


		# Config check for standard library config 
		Errors.__init__(self)
		Rooms.__init__(self)
		PluginLoader.__init__(self)


		# Load plugins 
		for i in self.getPlugins():
		    log.heading("Loading plugin " + i["name"])
		    self.loadPlugin(i).run(self, i['plugin_index'], i['priority_index'])


		self.dp.add_error_handler(self.error)

		self.updater.start_polling()






Natalia()


