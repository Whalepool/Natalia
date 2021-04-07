#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pprint import pprint 
import os 
from functools import partial
from utils.str import log
import datetime
from utils.str import Str, log
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

            try: 

                # If the chat_id is in our rooms list ...  
                if chat_id in self.n.config['rooms']: 

                    # Get the info /config for the room
                    room_data = self.n.config['rooms'][chat_id]

                    # if the room doesn't have save pictures set then get out 
                    if ('save_pictures' not in room_data) or (room_data['save_pictures'] == False):
                        return False 

                    
                    # Otherwise, get some data 
                    message_id = update.message.message_id 
                    user_id = update.message.from_user.id 
                    name = self.n.get_name(update)
                    timestamp = int(datetime.utcnow().strftime("%s"))
                    caption = update.message.caption
                    log.print('Saving picture posted by '+name+' in '+room_data['chat_name'])

                    # Picture has a caption ? 
                    if caption != None:
                        pass 

                    # Make some sizes we want to get 
                    do_pics = [
                        { 'suffix': 'small', 'size': 90, 'downloaded': False },
                        { 'suffix': 'large', 'size': 800, 'downloaded': False }
                    ]

                    total_pics = len(update.message.photo)
                    at_pic = 0 

                    # itterate through the different pictures 
                    for p in update.message.photo:

                        at_pic += 1 

                        # For each picture we're at check for if it matches the size 
                        for index, data in enumerate(do_pics):

                            # Check it hasn't... 
                            # 1) had this 'size' already downloaded
                            # 2) Check if its size meet our requirements
                            # 3) Or its the last most largest pic 
                            if (
                                    (do_pics[index]['downloaded'] == False) and
                                    (       
                                            (p.width == data['size']) or (p.height == data['size']) or (at_pic == total_pics)
                                    )
                                ):

                                    # Make a timestamp
                                    # epoch  = datetime.datetime.utcfromtimestamp(0)
                                    # know_utc = datetime.utcnow()
                                    # ts = int((now_utc - epoch).total_seconds())
                                    ts = int(datetime.utcnow().strftime("%s"))

                                    # Set the pic size to downloaded 
                                    do_pics[index]['downloaded'] = 1 

                                    # Make the path for the pic to sit in 
                                    local_path = self.n.config['path_pictures']+'/'+str(chat_id)
                                    full_path  = self.n.PATH+'/'+local_path+'/'
                                    fname = str(ts)+'-'+str(p.file_id)+'_'+data['suffix']+'.jpg'
                                    fpath = full_path+'/'+fname 

                                    # Download the pic
                                    pic = self.n.bot.getFile(p.file_id)
                                    pic.download(fpath)

                                    # Output log 
                                    log.print('Saving '+name+'\'s '+data['suffix']+' pic to: '+local_path+'/'+fname)


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
                                timestamp = int(datetime.utcnow().strftime("%s"))


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
