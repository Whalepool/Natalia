#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pprint import pprint 
import os 
from functools import partial
from utils.str import log
from datetime import datetime 
from PIL import Image
import traceback 
from telegram.ext import CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler, Filters




class Sticker_Handler:

	def __init__(self, Natalia, plugin_index, priority_index):

		self.n    = Natalia 
		self.data = self.n.config['plugins'][priority_index]['data']
		self.check_config_integrity()

		##############################################
		# END default, begin plugin
		##############################################

		log.heading2('Adding sticker hander look to Filters.sticker')
		self.n.dp.add_handler(MessageHandler(Filters.sticker, self.sticker_message), group=priority_index)


	def sticker_message(self, bot, update):

		try: 
			chat_id = update.message.chat.id

			if chat_id in self.n.config['rooms']: 

				# Get the info /config for the room
				room_data = self.n.config['rooms'][chat_id]

				# if the room doesn't have save pictures set then get out 
				if ('save_stickers' not in room_data) or (room_data['save_stickers'] == False):
					return False 

				
				# Otherwise, get some data 
				message_id = update.message.message_id 
				user_id = update.message.from_user.id 
				name = self.n.get_name(update)
				timestamp = datetime.now()
				sticker_id = update.message.sticker.file_id
				log.print('Saving sticker posted by '+name+' in '+room_data['chat_name'])

				# Make the path for the pic to sit in 
				local_path = self.n.config['path_stickers']
				full_path  = self.n.PATH+'/'+local_path+'/'
				fname = str(update.message.sticker.set_name)+'-'+sticker_id
				fpath = full_path+'/'+fname 

				
				tmp_fpath = self.n.PATH+'/'+self.n.config['path_tmp']+'/'+fname+'.webp'
				pic 	  = bot.getFile(sticker_id)
				pic.download(tmp_fpath)

				im = Image.open(tmp_fpath).convert("RGB")
				im.save(fpath+'.png',"png")

				log.print('Sticker saved to '+fpath+'.png')
				os.remove(tmp_fpath)


				# file = bot.getFile(sticker_id)
				# pprint(file.__dict__)
				
				# if username != None:
				# 	info = { 'user_id': user_id, 'chat_id': chat_id, 'message_id': message_id, 'sticker_id': sticker_id, 'timestamp': timestamp }
				# 	db.natalia_stickers.insert(info)

				# 	info = { 'user_id': user_id, 'name': name, 'username': username, 'last_seen': timestamp }
				# 	db.users.update_one( { 'user_id': user_id }, { "$set": info }, upsert=True)		
					

		except Exception as e:
			log.error(traceback.format_exc())


	


	def check_config_integrity(self):

		log.print('checking sticker handler config')
		# check       = ['phothandler']
		errors_list = []
		errors      = 0

		if len(self.n.config['rooms']) == 0:
			errors += 1
			errors_list.append('Error, no rooms in config. Rooms are needed because picture handling only takes place on designated moderation rooms')



		paths = self.n.config['path_stickers'].split('/')
		path = self.n.PATH 
		for p in paths:
			path += '/'+p 

			# Check is a directory 
			if os.path.isdir(path) == False:
				errors += 1
				errors_list.append('Error, directory: '+path+', does not exist')

			else: 
				if os.access(path, os.W_OK) == False:
					errors += 1
					errors_list.append('Error, directory: '+path+', is not writable')



		self.n.check_for_errors(errors, errors_list)



def run(Natalia, plugin_index, priority_index):

	return Sticker_Handler(Natalia, plugin_index, priority_index) 