#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pprint import pprint 
import os 
import yaml
from functools import partial
from utils.str import Str, log
import datetime
from dateutil.relativedelta import relativedelta
import random


from telegram.ext import CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler, Filters




class Welcome_Goodbye:

	def __init__(self, Natalia, plugin_index, priority_index):

		self.n    = Natalia 
		self.data = self.n.config['plugins'][plugin_index]['data']
		self.check_config_integrity()

		##############################################
		# END default, begin plugin
		##############################################

		log.heading2('Adding member join hook to new_chat_member')
		self.n.dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, self.new_chat_member), group=priority_index)

		log.heading2('Adding member leave hook to left_chat_member')
		self.n.dp.add_handler(MessageHandler(Filters.status_update.left_chat_member, self.left_chat_member), group=priority_index)





	def new_chat_member(self, bot, update):
		""" Welcomes new chat member """

		try: 

			lenchatmembers = len(update.message.new_chat_members)
			user_id    = update.message.new_chat_members[lenchatmembers-1].id 
			message_id = update.message.message_id 
			chat_id    = update.message.chat.id

			name = self.n.get_name(update)

			# Bot was added to a group chat
			joiner_is_self = False 
			if name == self.n.config['bot_name']:
				joiner_is_self = True 



			# Is a valid room we have settings for 
			if chat_id in self.n.config['rooms']:

				# Assign a variable to the room data
				room_data = self.n.config['rooms'][chat_id]

				# Log that we have a new user joining the room 
				log.heading(str(name)+' joined '+room_data['chat_name']+', '+room_data['chat_link']+', chat_id: '+str(chat_id))


				# Is a profile pic required ? 
				if room_data['profile_pic_required'] == True:

					# Get the users profile pics
					profile_pics = bot.getUserProfilePhotos(user_id=user_id)

					# If no profile pic...
					if profile_pics.total_count == 0:

						# Log it
						log.print(str(name)+' has no profile pic, restricting')

						# Delete any previous messages
						self.n.rooms_clear_last_self_msg(bot, chat_id)

						if room_data['welcome_users'] == True: 
							# Tell them the profile pic is required
							msg = update.message.reply_text(self.n.config['room_profile_pic_required_msg'].format(days=self.n.config['room_profile_pic_muting_days']))

							# Store this reply message_id as the last one we should delete when msging in public chats 
							self.n.config['rooms'][chat_id]['last_room_self_msg'] = msg.message_id

						now = datetime.now()
						rd = relativedelta(days=self.n.config['room_profile_pic_muting_days'])

						# Retrict them
						bot.restrict_chat_member(chat_id, user_id, until_date=(now + rd), can_send_messages=False, can_send_media_messages=False, can_send_other_messages=False, can_add_web_page_previews=False)	

						log.print('Restricting '+str(name)+' complete, end in '+str(self.n.config['room_profile_pic_muting_days'])+' days at '+str(now+rd))
						# end 
						return True 


				# User has a profile pic: Check. 
				# Are we auto restricting new users ? 
				if isinstance(room_data['restrict_new_users_days'], int):

					# Log it
					log.print(room_data['chat_name']+' chat rules, restricting')

					# Pick a random welcome message. 
					welcome_msg = random.choice(self.data['welcome'])

					if room_data['custom_welcome_msg'] != False:
						welcome_msg = room_data['custom_welcome_msg']

					# Delete any previous messages
					self.n.rooms_clear_last_self_msg(bot, chat_id)


					if room_data['welcome_users'] == True: 
						# Reply with the welcome message
						msg = welcome_msg.format(name=name)
						msg = update.message.reply_text(msg)

						# Store this reply message_id as the last one we should delete when msging in public chats 
						self.n.config['rooms'][chat_id]['last_room_self_msg'] = msg.message_id


					now = datetime.now()
					rd = relativedelta(days=room_data['restrict_new_users_days'])

					# Restrict them 
					bot.restrict_chat_member(chat_id, user_id, until_date=(now + rd), can_send_messages=False, can_send_media_messages=False, can_send_other_messages=False, can_add_web_page_previews=False)

					log.print('Restricting '+str(name)+' complete, end in '+str(room_data['restrict_new_users_days'])+' days at '+str(now+rd))
					return True 






			# Else, receiving data for a room with no config
			else: 
				log.error('New chat memeber in room '+str(chat_id)+' which is not in the rooms config')

				# User joined unknown chat who is not self 
				if name != self.n.config['bot_name']:

					# Get the chat info 
					chat_info = bot.getChat(chat_id)

					# Leave if setting set 
					if self.n.config['leave_chat_if_no_rooms_setting'] == True:
						log.error('Making bot leave chat '+chat_info.title )
						bot.leaveChat(chat_id)



				pprint(chat_info.__dict__)
				


		except Exception as e:
			log.error(traceback.format_exc())



		# if (chat_id == WP_ROOM) or (chat_id == SP_ROOM) or (chat_id == WP_WOMENS):
		# 	# Check user has a profile pic.. 

		# 	timestamp = datetime.datetime.utcnow()

		# 	info = { 'user_id': user_id, 'chat_id': chat_id, 'timestamp': timestamp }
		# 	db.room_joins.insert(info)





	def left_chat_member(self, bot, update):

		try: 

			user_id    = update.message.from_user.id
			chat_id    = update.message.chat.id 
			chat_name  = update.message.chat.title 
			chat_link  = update.message.chat.username 
			name       = self.n.get_name(update)



			# Is a valid room we have settings for 
			if chat_id in self.n.config['rooms']:

				# Assign a variable to the room data
				room_data = self.n.config['rooms'][chat_id]

				# Log that we have a new user joining the room 
				log.print(str(name)+' left  chat: '+room_data['chat_name']+', '+room_data['chat_link']+', chat_id: '+str(chat_id))

				# Delete any previous messages
				self.n.rooms_clear_last_self_msg(bot, chat_id)

				bye_msg = random.choice(self.data['goodbye'])
				if room_data['custom_bye_msg'] != False:
					bye_msg = room_data['custom_bye_msg']

				msg = bye_msg.format(name=name)

				msg = self.n.bot.sendMessage(chat_id=chat_id, text=msg,parse_mode="Markdown",disable_web_page_preview=1)
				self.n.config['rooms'][chat_id]['last_room_self_msg'] = msg.message_id


			# Else, receiving data for a room with no config
			else: 
				log.error(str(name)+' left  chat: '+chat_name+', @'+chat_link+', chat_id: '+str(chat_id))



		except Exception as e:
			log.error(traceback.format_exc())


		# pprint(update.message.chat.__dict__)
		# pprint(update.message.chat.__dict__)
		# pprint(update.message.from_user.__dict__)
		# pprint(update.message.left_chat_member.__dict__)


	def check_config_integrity(self):

		log.print('checking welcome_goodbye plugin config')
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

	return Welcome_Goodbye(Natalia, plugin_index, priority_index) 