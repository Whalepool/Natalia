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

                self.purge_start = None 

                ##############################################
                # END default, begin plugin
                ##############################################
                self.n.admins = self.data['users']

                # self.reply_command_regex = r"\/(ban|unban|readonly|nogifs)(?:\s+)([\dA-Za-z]+)"
                # self.n.dp.add_handler(MessageHandler( (Filters.reply & Filters.regex(self.reply_command_regex)), self.admin_replies), group=priority_index)
                
                self.reply_command_regex = r"\/purgejoins"
                self.n.dp.add_handler(MessageHandler( (Filters.reply & Filters.regex(self.reply_command_regex)), self.purge_joins), group=priority_index)


        def purge_joins(self, update, bot):

            
            attempt_user_id = update.message.from_user.id
            
            self.purge_start = { 
                'message_id': update.message.reply_to_message.message_id,
                'chat_id': update.message.reply_to_message.chat.id
            }
                
            try: 
                room_data = self.n.config['rooms'][update.message.reply_to_message.chat.id]
                chat_name = room_data['chat_name']
            except Exception as e:
                pprint(e)
                chat_name = chat_id 

            try: 
                if attempt_user_id not in self.n.admins:
                    log.error('Invalid purge attempt from %s(%s) in %s(%s)' % (
                        update.message.from_user.username,
                        attempt_user_id,
                        update.message.chat.id,
                        chat_name
                    ))
                    return 
            except Exception as e:
                pprint(e)
                pass 


            try:
                action = list(self.n.db.welcome_joins.find({'message_id': { '$gt': self.purge_start['message_id'] }, 'chat_id': self.purge_start['chat_id']}))

                now = datetime.datetime.now()
                rd = relativedelta(days=400)
                perms = ChatPermissions(can_send_messages=False, can_send_media_messages=False, can_send_polls=False, can_send_other_messages=False, can_add_web_page_previews=False, can_change_info=False, can_invite_users=True, can_pin_messages=False)
                for a in action:
                    try:
                        if a['user_id'] not in self.n.admins:
                            self.n.bot.restrict_chat_member( a['chat_id'], a['user_id'], perms, until_date=(now + rd))      
                            log.print('PurgeJoins: restricting user %s in %s(%s)' % ( a['user_id'], chat_name, a['chat_id']))
                        else:
                            log.error('PurgeJoins: skipping restricting user %s as user is an admin' % (a['user_id']))
                        
                    except Exception as e:
                        log.error('PurgeJoins: Unable to restrict chat member %s in %s(%s), insufficient permissions' % (a['user_id'],chat_name, a['chat_id']))


                    try:

                        self.n.bot.delete_message(chat_id=a['chat_id'], message_id=a['message_id'])
                        log.print('PurgeJoins: Deleting join message of user %s in %s(%s)' % (a['user_id'], chat_name, a['chat_id']))

                        self.db.welcome_joins.delete({'message_id':a['message_id'],'chat_id':a['chat_id']})

                    except Exception as e:
                        log.error('PurgeJoins: Unable to delete message %s in %s(%s), maybe already deleted/permissions' % (a['message_id'], chat_name, a['chat_id']))


            except Exception as e:
                pprint(e)
                log.error('Error purging joins')

#
        # def start(self, bot, update):

        #       user_id = update.message.from_user.id 
        #       if user_id not in self.data['users']:
        #               return False 

        #       chat_id    = update.message.chat.id

        #       self.n.bot.sendMessage(chat_id=chat_id, text='You are an admin for this bot',parse_mode="Markdown",disable_web_page_preview=1)


        def admin_replies(self, update, bot):

                print('here!!!')

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
