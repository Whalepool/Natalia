#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pprint import pprint 
import os 
from functools import partial
from utils.str import log
import re 
from telegram.ext import CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler, Filters




class Admins:

        def __init__(self, Natalia, plugin_index, priority_index):

                self.n    = Natalia 
                self.data = self.n.config['plugins'][plugin_index]['data']
                self.check_config_integrity()

                ##############################################
                # END default, begin plugin
                ##############################################
                self.n.admins = self.data['users']

                self.reply_command_regex = r"\/(ban|unban|readonly|nogifs)(?:\s+)([\dA-Za-z]+)"
                self.n.dp.add_handler(MessageHandler( (Filters.reply & Filters.regex(self.reply_command_regex)), self.admin_replies), group=priority_index)



        # def start(self, bot, update):

        #       user_id = update.message.from_user.id 
        #       if user_id not in self.data['users']:
        #               return False 

        #       chat_id    = update.message.chat.id

        #       self.n.bot.sendMessage(chat_id=chat_id, text='You are an admin for this bot',parse_mode="Markdown",disable_web_page_preview=1)


        def admin_replies(self, update, bot):


                chat_id = update.message.chat.id
                if  chat_id not in [-1001223115449, -238862165]:
                        return False 

                replyer_user_id = update.message.from_user.id 
                replyer_username = update.message.from_user.username 
                replyer_message = update.message.text           

                if replyer_user_id not in self.n.admins:
                        return False 


                matches = re.findall(r"\/(ban|unban|readonly|nogifs)(?:\s+)([\dA-Za-z]+)(?:\s+)([\dA-Za-z]+)", replyer_message)

                if len(matches) == 1:

                        command = matches[0][0]
                        scope = matches[0][1]
                        length = matches[0][2]

                else:
                        matches = re.findall(r"\/(ban|unban|readonly|nogifs)(?:\s+)([\dA-Za-z]+)", replyer_message)
                        command = matches[0][0]
                        scope = 'global'
                        length = matches[0][1]



                string = command+' - '+scope+' - '+length

                pprint(string)
                self.n.bot.sendMessage(chat_id=chat_id, text=string)
                # pprint(command)
                # pprint(scope)
                # pprint(length)


                if update.message.reply_to_message.forward_from is not None: 
                        user_id = update.message.reply_to_message.forward_from.id
                        name    = update.message.reply_to_message.forward_from.first_name 
                        message_id = update.message.reply_to_message.message_id 
                        chat_id = update.message.reply_to_message.chat.id 



                # else:
                #       user_id = update.message.reply_to_message.from_user.id
                #       name    = update.message.reply_to_message.from_user.first_name 
                #       message_id = update.message.reply_to_message.message_id 
                #       chat_id = update.message.reply_to_message.chat_id   

                #       pprint(update.message.reply_to_message.__dict__)                        



        def check_config_integrity(self):


                log.print('checking admin plugin config')

                errors_list = []
                errors      = 0

                if 'users' not in self.data:
                        errors += 1
                        errors_list.append('Missing users in config.plugins.[x].admins.users')

                self.n.check_for_errors(errors, errors_list)

                return 



def run(Natalia, plugin_index, priority_index):

        return Admins(Natalia, plugin_index, priority_index) 
