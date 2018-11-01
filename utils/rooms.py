
# Datetime
import json  
from os.path import basename 

from pprint import pprint 
from utils.str import Str, log


class Rooms:

	def __init__(self):	

		# Check the room config 
		self.rooms_check_config_integrity()

		return True 




	def rooms_clear_last_self_msg(self, bot, chat_id):


		if 'last_room_self_msg' not in self.config['rooms'][chat_id]:
			return True 

		if type(self.config['rooms'][chat_id]['last_room_self_msg']) is not int:
			log.error('Tried to delete last chat message but messagee_id was not int: '+str(self.config['rooms'][chat_id]['last_room_self_msg']))
			return True 

		message_id = self.config['rooms'][chat_id]['last_room_self_msg']
		bot.delete_message(chat_id=chat_id, message_id=message_id)




	def rooms_check_config_integrity(self):

		log.heading2('Checking room settings are valid and complete...')
		errors_list = []
		errors = 0

		if 'room_profile_pic_required_msg' not in self.config:
			errors += 1
			errors_list.append('missing config.room_profile_pic_required_msg (str)')
		elif type(self.config['room_profile_pic_required_msg']) is not str:
			errors += 1
			errors_list.append('config.room_profile_pic_required_msg needs to be a string')


		if 'room_profile_pic_muting_days' not in self.config:
			errors += 1 
			errors_list.append('missing config.room_profile_pic_muting_days (int)')
		elif type(self.config['room_profile_pic_muting_days']) is not int:
			errors += 1 
			errors_list.append('config.room_profile_pic_muting_days need to be an integer')

		self.check_for_errors(errors, errors_list)


		for chat_id, data in self.config['rooms'].items():


			log.print('Checking chat_id '+str(chat_id)+' config')

			# Check the chat id is and int, if it is, fine...
			if isinstance(chat_id, int):
				pass

			# IF the chat id is a string, then it must start  with a "@" for a room name
			if isinstance(chat_id, str):
				if chat_id[0] is not '@':
					errors += 1
					errors_list.append('chat id is not valid, must be either int, positive or negative, or start with a "@" sign.')


			if 'chat_name' not in data:
				errors += 1
				errors_list.append('missing chat_name')

			if 'chat_link' not in data:
				errors += 1
				errors_list.append('missing chat_link, eg: @myroom')
			else:
				if data['chat_link'][0] != '@':
					errors += 1
					errors_list.append('chat id is not valid, must be either int, positive or negative, or start with a "@" sign.')


			if 'profile_pic_required' not in data:
				errors += 1
				errors_list.append('missing profile_pic_required (True,False)')
			else:
				if (type(data['profile_pic_required'])) is not bool:
					errors += 1
					errors_list.append('profile_pic_required must be either True, or False (bool)')

			if 'restrict_new_users_days' not in data:
				errors += 1
				errors_list.append('missing restrict_new_users_days (False or int of days for new users to be restricted for)')
			else:
				if data['restrict_new_users_days'] == False:
					pass
				elif type(data['restrict_new_users_days']) is not int:
					errors += 1
					errors_list.append('restrict_new_users_days should be set to  (False or int of days for new users to be restricted for)')

			if 'log_messages' not in data:
				errors += 1
				errors_list.append('missing log_messages (True,False)')
			else:
				if (type(data['log_messages'])) is not bool:
					errors += 1
					errors_list.append('log_messages must be either True, or False (bool)')

			if 'custom_welcome_msg' not in data:
				errors += 1
				errors_list.append('missing custom_welcome_msg (False or str of custom welcome message)')
			else:
				if data['custom_welcome_msg'] == False:
					pass
				elif type(data['custom_welcome_msg']) is not str:
					errors += 1
					errors_list.append('custom_welcome_msg should be set to  (False or str of custom welcome message)')

			if 'custom_bye_msg' not in data:
				errors += 1
				errors_list.append('missing custom_bye_msg (False or str of custom bye message)')
			else:
				if data['custom_bye_msg'] == False:
					pass
				elif type(data['custom_bye_msg']) is not str:
					errors += 1
					errors_list.append('custom_bye_msg should be set to  (False or str of custom bye message)')


			# STILL TO VERIFY 
		    # feed_room_id: '@whalepoolbtcfeed'
		    # channel_type: 'group'

		self.check_for_errors(errors, errors_list)
