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
            self.n.dp.add_handler(CommandHandler('test', self.test))

            self.n.dp.add_handler(MessageHandler(Filters.text & ~Filters.command, self.echo_pm), group=priority_index)

        def test( self, update, callback):
            pass 
            # pprint(update.message.from_user.__dict__)
            # self.n.bot.sendMessage(chat_id=61697695, text='hello world',parse_mode="Markdown",disable_web_page_preview=1)

        def check_config_integrity(self):
            pass 


        def echo_pm(self, update, callback):
            """ Echo's a PM message"""

#            print('echo pm: %s ' % (__file__ ))
#            pprint('update.message.__dict__')
#            pprint(update.message.__dict__)
#            pprint('update.message.from_user.__dict__)')
#            pprint(update.message.from_user.__dict__)
#            pprint('update.message.chat.__dict__')
#            pprint(update.message.chat.__dict__)
#
            try:
                name = self.n.get_name(update)

                if update['channel_post'] is not None:
                    pprint(update.channel_post.__dict__)

                elif update['edited_message'] is not None:

                    chat_id = update.edited_message.chat.id 
                    chat = update.edited_message.chat
                    message_id = update.edited_message.message_id
                    text = update.edited_message.text 

                    msg = 'EDITED PM: %s, messageid(%s), chat_id(%s), first_name(%s), username(@%s) edited message to (%s)' % (
                        __file__, message_id, chat_id, chat.first_name, chat.username, text ) 

                else: 
                    chat_id    = update.message.chat.id
                    chat = update.message.chat

                    message_id = update.message.message_id 
                    text = update.message.text

                    msg = 'PM: %s, messageid(%s),chat_id(%s), firstname(%s) username(@%s) in pm said: %s' % (
                        __file__, message_id, chat_id, chat.first_name, chat.username, text  )

                if chat.type == 'private': 
                    log.print(msg) 
                    self.n.check_user_exists( chat_id, chat.first_name, chat.username ) 


            except Exception as e:
                log.error(traceback.format_exc())
                pprint(update.__dict__)


def run(Natalia, plugin_index, priority_index):

        ##############################################
        # SET THIS TO UR PLUGINS CLASSNAME 
        return PM_Logger(Natalia, plugin_index, priority_index) 
