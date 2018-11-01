#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pprint import pprint 
import os 
from functools import partial
from utils.str import log

from telegram.ext import CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler, Filters




class Blank_Plugin_Class_Name:

	def __init__(self, Natalia, plugin_index, priority_index)

		self.n    = Natalia 
		self.data = self.n.config['plugins'][priority_index]['data']
		self.check_config_integrity()

		##############################################
		# END default, begin plugin
		##############################################

		# log.heading2('Some event handler log output')
		# self.n.dp.add_handler( .. , group=priority_index)



	def check_config_integrity(self):

		log.heading2('log output that plugin is going to check confi')
		check       = ['welcome','goodbye']
		errors_list = []
		errors      = 0

		for check_type in check: 
			if check_type not in self.data:
				errors += 1
				errors_list.append('Missing '+check_type+' messages in config')

			elif type(self.data[check_type]) is not list:
				errors += 1
				errors_list.append('No '+check_type+' messages found')

			else:
				if (self.data[check_type][0] == ''):
					errors += 1
					errors_list.append('First '+check_type+' message is empty')

		self.n.check_for_errors(errors, errors_list)




def run(Natalia, plugin_index, priority_index):

	return Blank_Plugin_Class_Name(Natalia, plugin_index, priority_index) 