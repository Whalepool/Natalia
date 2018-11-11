#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pprint import pprint 
import os 
from functools import partial
from utils.str import log

from telegram.ext import CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler, Filters



##############################################
# EDIT THIS FUNCTION NAME TO BE UR PLUGIN CLASS NAME
class Blank_Plugin_Class_Name:

	def __init__(self, Natalia, plugin_index, priority_index):

		self.n    = Natalia 
		self.data = self.n.config['plugins'][priority_index]['data']
		self.check_config_integrity()

		##############################################
		# ADD HOOKS HERE 

		# log.heading2('Some event handler log output')
		# self.n.dp.add_handler( .. , group=priority_index)



	def check_config_integrity(self):

		log.print('Checking XXXX plugin config requirements ')


		# Some list of vars to check 
		check       = ['some-example-requirement']

		# List of error messages to report back on plugin config checking failure 
		errors_list = []

		# error counter 
		errors      = 0

		# self.data contains the plugin data from the config file

		# eg: 
		# If the variable we want to check for isn't in the plugin config data 
		# if check[0] not in self.data:

		# 	Log the error
		# 	errors_list.append('the variable in check list was not found in plugin config data')
		#	errors += 1

		# Check we dont have any errors loading the plugin config 
		# self.n.check_for_errors(errors, errors_list)




def run(Natalia, plugin_index, priority_index):

	##############################################
	# SET THIS TO UR PLUGINS CLASSNAME 
	return Blank_Plugin_Class_Name(Natalia, plugin_index, priority_index) 