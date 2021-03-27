#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pprint import pprint 
import os 
from functools import partial
from utils.str import log

from telegram.ext import CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler, Filters



##############################################
# EDIT THIS FUNCTION NAME TO BE UR PLUGIN CLASS NAME
class PM_Logger:

        def __init__(self, Natalia, plugin_index, priority_index):

            self.n    = Natalia 
            self.data = self.n.config['plugins'][priority_index]['data']
            self.check_config_integrity()

            ##############################################
            # ADD HOOKS HERE 
            self.n.dp.add_handler(MessageHandler(Filters.text & ~Filters.command, self.echo_pm), group=priority_index)


        def check_config_integrity(self):
            pass 


        def echo_pm(self, bot, update):
            """ Echo's a PM message"""

            try:
                message_id = update.message.message_id 
                chat_id    = update.message.chat.id

                name = self.n.get_name(update)
                chat = update.message.chat
                text = update.message.text

                if chat.type == 'private': 
                    log.print('messageid(%s),chat_id(%s), firstname(%s) username(@%s) in pm said: %s' % (
                        message_id, chat_id, chat.first_name, chat.username, text  ))


            except Exception as e:
                log.error(traceback.format_exc())
                print(update.message.__dict__)




def run(Natalia, plugin_index, priority_index):

        ##############################################
        # SET THIS TO UR PLUGINS CLASSNAME 
        return PM_Logger(Natalia, plugin_index, priority_index) 
