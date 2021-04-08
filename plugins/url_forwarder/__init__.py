#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pprint import pprint 
import os 
from functools import partial
from utils.str import log

from telegram.ext import CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler, Filters
from telegram import MessageEntity, TelegramObject, ChatAction

class URL_Forwarder:

    def __init__(self, Natalia, plugin_index, priority_index):

        self.n    = Natalia 
        self.data = self.n.config['plugins'][priority_index]['data']
        self.check_config_integrity()

        ##############################################
        # ADD HOOKS HERE 

        self.n.dp.add_handler(MessageHandler(Filters.entity(MessageEntity.URL), self.forward_links), group=priority_index)

    def forward_links( self, update, callback):

        user_id = update.message.from_user.id 
        message_id = update.message.message_id 
        chat_id = update.message.chat.id
        room_data = self.n.config['rooms'][chat_id]
        name = self.n.get_name(update)
        
        try:
            feed_room_id = room_data['feed_room_id']
        except Exception:
            return 

        furlcnt = re.findall(self.n.config['forwarding_urls'], update.message.text)
        forward = False 
        if len(furlcnt) > 0:
            forward = feed_room_id 
        else:
            forward = 61697695
            
        # if forward != False:
        self.n.bot.forwardMessage(chat_id=forward, from_chat_id=chat_id, message_id=message_id)


    def check_config_integrity(self):
        pass 
    
def run(Natalia, plugin_index, priority_index):

        ##############################################
        # SET THIS TO UR PLUGINS CLASSNAME 
        return URL_Forwarder(Natalia, plugin_index, priority_index) 
