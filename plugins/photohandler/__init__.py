#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pprint import pprint 
import os 
from functools import partial
from utils.str import log
from utils.str import Str, log
import time
from telegram.ext import CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler, Filters

import traceback 


class Photo_Handler:

    def __init__(self, Natalia, plugin_index, priority_index):

        self.n    = Natalia 
        self.data = self.n.config['plugins'][priority_index]['data']
        self.check_config_integrity()


        ##############################################
        # END default, begin plugin
        ##############################################

        # Pictures
        log.heading2('Adding photo hander look to Filters.photo')
        self.n.dp.add_handler(MessageHandler(Filters.photo, self.photo_message), group=priority_index)
        
        # Documents 
        log.heading2('Adding picture hander look to Filters.document')
        self.n.dp.add_handler(MessageHandler(Filters.document, self.document_picture), group=priority_index)



    def photo_message(self, update, bot):

        try: 
            chat_id = update.message.chat.id
        except Exception as e:
            log.error(traceback.format_exc())
            print(update.message.__dict__)

        # If the chat_id is in our rooms list ...  
        if chat_id not in self.n.config['rooms']: 
            return 

        try: 
            # Get the info /config for the room
            room_data = self.n.config['rooms'][chat_id]

            # if the room doesn't have save pictures set then get out 
            if ('save_pictures' not in room_data) or (room_data['save_pictures'] == False):
                return False 

            
            # Otherwise, get some data 
            message_id = update.message.message_id 
            user_id = update.message.from_user.id 
            name = self.n.get_name(update)
            photo_id = update.message.photo[0].file_id
            timestamp = int(time.time())
            caption = update.message.caption
            log.print('Saving picture posted by '+name+' in '+room_data['chat_name'])

            info = { 'user_id': user_id, 'chat_id': chat_id, 'message_id': message_id, 'photo_id': photo_id, 'text': caption, 'timestamp': timestamp }
            self.n.db.photos.insert(info)
            self.n.update_user( user_id, {'last_photo': photo_id } )
            
            # pprint(update.message.__dict__)
            # pprint(update.message.photo[0].__dict__)




        except Exception as e:
            log.error(traceback.format_exc())



    def document_picture(self, update, bot):

        try: 
                chat_id = update.message.chat.id

                if chat_id in self.n.config['rooms']: 

                        room_data = self.n.config['rooms'][chat_id]
                        
                        message_id = update.message.message_id 
                        user_id = update.message.from_user.id 
                        name = self.n.get_name(update)
                        timestamp = int(time.time())


                        images = ['image/jpeg','image/png']
                        if update.message.document.mime_type in images:

                                log.print(str(name)+' uploaded a picture in a compressed format to '+room_data['chat_name'])

                                # Delete any previous messages
                                self.n.rooms_clear_last_self_msg(chat_id)

                                # delete the uploaded pic
                                self.n.bot.delete_message(chat_id=chat_id, message_id=message_id)
                                log.print('deleted offending uncompressed pic')

                                # Msg that the pic got deleted
                                msg = self.n.bot.sendMessage(chat_id=chat_id, text=name+", I deleted that pic you just posted because it is an uncompressed format, please use the \'compress\' format when posting pictures.",parse_mode="Markdown",disable_web_page_preview=1)
                                log.print('messaged '+name+' notifying of deletion')
                                self.n.config['rooms'][chat_id]['last_room_self_msg'] = msg.message_id
                                

        except Exception as e:
                log.error(traceback.format_exc())


    def check_config_integrity(self):

            log.print('checking photo handler config')
            # check       = ['phothandler']
            errors_list = []
            errors      = 0

            if len(self.n.config['rooms']) == 0:
                    errors += 1
                    errors_list.append('Error, no rooms in config. Rooms are needed because picture handling only takes place on designated moderation rooms')



            paths = self.n.config['path_pictures'].split('/')
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


            for chat_id, data in self.n.config['rooms'].items():
                    chat_id_path =path+'/'+str(chat_id)

                    if ('save_pictures' in data) and (data['save_pictures'] == True):

                            # Check is a directory 
                            if os.path.isdir(chat_id_path) == False:
                                    log.error('Warning, pictures directory for '+data['chat_name']+', '+chat_id_path+', does not exist and `save_pictures` is enabled to True for this room')

                            else: 
                                    if os.access(chat_id_path, os.W_OK) == False:
                                            errors += 1
                                            errors_list.append('Error, directory for '+data['chat_name']+', '+chat_id_path+', is not writable')



            self.n.check_for_errors(errors, errors_list)




def run(Natalia, plugin_index, priority_index):

        return Photo_Handler(Natalia, plugin_index, priority_index) 
