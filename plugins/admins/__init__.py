#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pprint import pprint 
import os 
from functools import partial
from utils.str import log

from telegram.ext import CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler, Filters




class Admins:

	def __init__(self, Natalia, plugin_index, priority_index):

		self.n    = Natalia 
		self.data = self.n.config['plugins'][plugin_index]['data']
		self.check_config_integrity()

		##############################################
		# END default, begin plugin
		##############################################
		self.n.admins = self.data['users']

		#log.heading2('Loading admin /start menu hooks')
		#self.n.dp.add_handler(CommandHandler('start',  self.start ), group=priority_index )


	# def start(self, bot, update):

	# 	user_id = update.message.from_user.id 
	# 	if user_id not in self.data['users']:
	# 		return False 

	# 	chat_id    = update.message.chat.id

	# 	self.n.bot.sendMessage(chat_id=chat_id, text='You are an admin for this bot',parse_mode="Markdown",disable_web_page_preview=1)




	def check_config_integrity(self):


		log.print('checking admin plugin config')

		errors_list = []
		errors      = 0

		if 'users' not in self.data:
			errors += 1
			errors_list.append('Missing users in config.plugins.[x].admins.users')

		self.n.check_for_errors(errors, errors_list)

		return 



def run(Natalia, plugin_index, priority_index):

	return Admins(Natalia, plugin_index, priority_index) 