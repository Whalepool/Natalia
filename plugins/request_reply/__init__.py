#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pprint import pprint 
import os 
import yaml
from functools import partial
from utils.str import Str, log


from telegram.ext import CommandHandler, ConversationHandler, CallbackQueryHandler




class Request_Reply:

	def __init__(self, Natalia, plugin_index, priority_index):

		self.n    = Natalia 
		self.data = self.n.config['plugins'][plugin_index]['data']
		self.check_config_integrity()

		##############################################
		# END default, begin plugin
		##############################################

		for i in self.data:
			log.heading2('Adding /'+str(i['request']))
			self.n.dp.add_handler(
				CommandHandler(
					i['request'],  
					partial(self.reply, msg=i['reply'], allow_in_group_chat=i.get('allow_in_group_chat', False) )
				),
				group=priority_index 
			)



	def reply(self, bot, update, msg, allow_in_group_chat):


		# Get the users name 
		name = self.n.get_name(update)
		user_id = update.message.from_user.id 
		chat_id = update.message.chat.id
		message_id = update.message.message_id



		################################################
		# LOG
		log.print(str(update.message.text)+' - '+str(name)+', user_id: '+str(user_id)+', from chat_id: '+str(chat_id)+' - '+update.message.chat.type)
		#
		################################################

		if (allow_in_group_chat == False) and  (
				(update.message.chat.type == 'group') or 
				(update.message.chat.type == 'supergroup')
			):


			# Delete any previous messages
			self.n.rooms_clear_last_self_msg(bot, chat_id)

			# Tell them the profile pic is required
			msg = update.message.reply_text(self.n.config['room_no_cmd_in_public_chat_msg'].format(name=name))

			# Store this reply message_id as the last one we should delete when msging in public chats 
			self.n.config['rooms'][chat_id]['last_room_self_msg'] = msg.message_id

			
			return False 
		


		# See what kind of reply actions need to be taken 
		# Is a list of replying actions 
		if type(msg) is list:
			for r in msg:

				# Regular replying msg 
				if 'msg' in r: 
					msg = r['msg'].format(name=name, first='A')
					self.n.bot.sendMessage(chat_id=chat_id, text=msg,parse_mode="Markdown",disable_web_page_preview=1)

				# Sticker reply
				if 'sticker' in r: 
					bot.sendSticker(chat_id=chat_id, sticker=r['sticker'], disable_notification=False)

		# Is a singular reply 
		else: 
			msg = msg.format(name=name, first='A')
			self.n.bot.sendMessage(chat_id=chat_id, text=msg,parse_mode="Markdown",disable_web_page_preview=1)



	def getid(self, bot, update):

		pprint(update.message.chat.__dict__, indent=4)
		update.message.reply_text(str(update.message.chat.first_name)+" :: "+str(update.message.chat.id))

		self.n.bot.sendMessage(chat_id=chat_id, text='test',parse_mode="Markdown",disable_web_page_preview=1)


	def check_config_integrity(self):

		log.print('checking request_reply plugin config')
		pass 


def run(Natalia, plugin_index, priority_index):

	return Request_Reply(Natalia, plugin_index, priority_index) 