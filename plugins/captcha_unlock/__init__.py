#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pprint import pprint 
import os 
from functools import partial
from utils.str import log

import datetime
from telegram.ext import CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler, Filters
from telegram import ForceReply

import random
import string
from PIL import Image
from claptcha import Claptcha


def randomString():
   return str(random.randint(5000, 10000))
 


##############################################
# EDIT THIS FUNCTION NAME TO BE UR PLUGIN CLASS NAME
class Captcha_Unlock:

        def __init__(self, Natalia, plugin_index, priority_index):
            
            self.n    = Natalia 
            self.data = self.n.config['plugins'][plugin_index]['data']
            self.check_config_integrity()
            self.captcha = Claptcha(randomString, './fonts/Roboto-Regular.ttf', (200,100),
             resample=Image.BICUBIC, noise=0.5)

            ##############################################
            # ADD HOOKS HERE 
            log.heading2('Adding /start captcha request')
            self.n.dp.add_handler(
                CommandHandler(
                        'start',  
                        self.start_command_check
                ),
                group=priority_index 
            )

            self.n.dp.add_handler(MessageHandler(Filters.text & ~Filters.command, self.check_captcha_reply), group=priority_index)

        def check_config_integrity(self):
            pass 

        def send_captcha( self, user_id, chat_id, info={}):

            timestamp = datetime.datetime.utcnow()
            info.update( {'last_seen': timestamp } )
            
            fpath = 'data/tmp/captcha_%s.png' % user_id 
            text, _ = self.captcha.write(fpath)
            
            log.print('Send captcha to %s with captcha text %s' % (user_id, text) 
            photo_msg = self.n.bot.send_photo(chat_id, photo=open(fpath, 'rb'), reply_markup=ForceReply(force_reply=True))
 
            info.update( {'captcha_text': text, 'captcha_message_id': photo_msg.message_id })
            self.n.update_user( user_id, info ) 


        def check_captcha_reply(self, update, callback):

            if update.message is None:
                return 

            if update.message.reply_to_message is None:
                return

            chat_id = update.message.chat.id
            user_id = update.message.from_user.id
            message_id = update.message.reply_to_message.message_id

            f_name = update.message.chat.first_name
            name = f_name 
            username = update.message.chat.username

            self.n.check_user_exists( user_id, name, username )

            if 'captcha_message_id' not in self.n.users[user_id]:
                return 

            if message_id == self.n.users[user_id]['captcha_message_id']:

                if update.message.text == self.n.users[user_id]['captcha_text']:

                    self.n.update_user( user_id, {'captcha_complete': 1} )

                    derestrict_rooms = []
                    try:
                        for cid, restriction_type in self.n.users[user_id]['rooms'].items():
                            if restriction_type == 'auto_restrict':
                                derestrict_rooms.append(int(cid))
                    except Exception:
                        pass

                    if len(derestrict_rooms) > 0:
                        for room_id in derestrict_rooms:  
                            room_data = self.n.config['rooms'][room_id]
                            perms = ChatPermissions(
                                    can_send_messages=True,
                                    can_send_media_messages=True,
                                    can_send_polls=True, 
                                    can_send_other_messages=True,
                                    can_add_web_page_previews=True, 
                                    can_change_info=False,
                                    can_invite_users=True, 
                                    can_pin_messages=False
                                )
                            try: 
                                log.print('Removing restrictions from %s for %s' % (room_data['chat_name'], user_id ))
                                self.n.bot.restrict_chat_member(room_id, user_id, perms )        
                                self.n.update_user_room( user_id, chat_id, 'no_restrictions') 
                            except Exception:
                                log.error('Unable to remove restrictions in %s due to insufficient permissions' % room_data['chat_name'])
                    
                    self.n.bot.sendMessage(chat_id=chat_id, text=self.data['correct_msg'], parse_mode='Markdown', disable_web_page_preview=1)

                else:
                    
                    self.n.bot.sendMessage(chat_id=chat_id, text=self.data['incorrect_msg'], parse_mode='Markdown', disable_web_page_preview=1)

                    self.send_captcha( user_id, chat_id ) 




        def start_command_check(self, update, callback):

            if update.message.chat.type != 'private':
                return 
            
            chat_id = update.message.chat.id
            user_id = chat_id 

            try:
                if self.n.users['user_id']['captcha_complete'] == 1:
                    return
            except Exception:
                pass 

            f_name = update.message.chat.first_name
            name = f_name 
            username = update.message.chat.username

            self.n.check_user_exists( user_id, name, username )

            send_captcha = False 
            info = {} 

            if 'captcha_complete' not in self.n.users[user_id]:
                send_captcha = True 

            if send_captcha == True: 

                self.n.bot.sendMessage(chat_id=chat_id, text=self.data['start_msg'], parse_mode='Markdown', disable_web_page_preview=1)
                self.send_captcha( user_id, chat_id )
                
                return



def run(Natalia, plugin_index, priority_index):

        ##############################################
        # SET THIS TO UR PLUGINS CLASSNAME 
        return Captcha_Unlock(Natalia, plugin_index, priority_index) 
