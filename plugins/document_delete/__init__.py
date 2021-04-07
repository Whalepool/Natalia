#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pprint import pprint 
import os 
from functools import partial
from utils.str import log

from telegram.ext import CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler, Filters




class Document_Delete:

        def __init__(self, Natalia, plugin_index, priority_index):

            self.n    = Natalia 
            self.data = self.n.config['plugins'][priority_index]['data']
            self.check_config_integrity()

            ##############################################
            # END default, begin plugin
            ##############################################

            # log.heading2('Some event handler log output')
            # self.n.dp.add_handler( .. , group=priority_index)
            self.n.dp.add_handler(MessageHandler((
                Filters.document.apk | 
                Filters.document.application |
                Filters.document.doc | 
                Filters.document.docx | 
                Filters.document.exe | 
                Filters.document.py | 
                Filters.document.svg | 
                Filters.document.targz | 
                Filters.document.zip 
                ), self.del_document), group=priority_index)


        def del_document(self, update, callback):


                user_id = update.message.from_user.id
                chat_id = update.message.chat_id
                message_id = update.message.message_id
                name = self.n.get_name(update)

                # If users an admin, exit
                if user_id in self.admins:
                        return False 

                # Room isn't in our config, exit
                if chat_id not in self.n.config['rooms']:
                        log.error('File posted in a chat/room we have no config for')
                        return False

                # Get the room info
                room_data = self.n.config['rooms'][chat_id]

                # No auto delete config set, exit
                if 'auto_delete_posted_files' not in room_data:
                        return False 

                # auto delete config is set, but set to false, exit
                if room_data['auto_delete_posted_files'] == False:
                        return False 


                # Message the chat saying posting files is not allowed 
                self.n.bot.sendMessage(chat_id=chat_id, text=name+", posting files is not allowed in this room, so I deleted it, details have been forwarded to mods for review.",parse_mode="Markdown",disable_web_page_preview=1)
                self.n.bot.sendMessage(chat_id=self.admin_room_id, text=name+' posted a file in '+room_data['chat_name'])
                self.n.bot.forward_message(chat_id=self.admin_room_id, from_chat_id=chat_id, message_id=message_id)
                self.n.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)



        def check_config_integrity(self):

                log.print('Checking document_delete plugin config requirements ')


                # Some list of vars to check 
                rooms = self.n.config['rooms']

                # List of error messages to report back on plugin config checking failure 
                errors_list = []

                # error counter 
                errors      = 0

                found  = 0 

                # Search rooms config to see if any rooms have this plugin enabled
                for chat_id,data in rooms.items():
                        if 'auto_delete_posted_files' in data:
                                if data['auto_delete_posted_files'] == True:
                                        log.print('Found \'auto_delete_posted_files\' for '+data['chat_name'])
                                        found = 1


                # Could not find any rooms with this feature enabled 
                if found != 1:
                        errors_list.append('No rooms found with \'auto_delete_posted_files\' set to True, disable plugin then restart')
                        errors += 1 


                # Make sure admin plugin is enabled and is #1 plugin
                if self.n.config['plugins'][0]['name'] == 'admins':
                        self.admins = self.n.config['plugins'][0]['data']['users']

                        # Make sure we have a mod room set
                        if 'admin_room_id' in self.n.config['plugins'][0]['data']:
                                self.admin_room_id  = self.n.config['plugins'][0]['data']['admin_room_id']


                                if self.admin_room_id in self.n.config['rooms']:
                                        self.admin_room = self.n.config['rooms'][self.admin_room_id]
                                else:
                                        errors_list.append('No admin room is set ( chat id: '+str(self.admin_room_id)+') in the rooms config')
                                        errors += 1 

                        else:
                                errors_list.append('No admin_room_id set in the admins plugin')
                                errors += 1 

                else:
                        errors_list.append('Admnins plugin must be enabled and the first plugin listed')
                        errors += 1



                # Check we dont have any errors loading the plugin config 
                self.n.check_for_errors(errors, errors_list)




def run(Natalia, plugin_index, priority_index):


        return Document_Delete(Natalia, plugin_index, priority_index) 
