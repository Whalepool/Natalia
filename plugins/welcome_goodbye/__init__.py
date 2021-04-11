#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pprint import pprint 
import os 
import yaml
from functools import partial
from utils.str import Str, log
import datetime
from dateutil.relativedelta import relativedelta
import random
import traceback 

from telegram.ext import CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler, Filters
from telegram.utils import helpers
from telegram import ChatPermissions



class Welcome_Goodbye:

        def __init__(self, Natalia, plugin_index, priority_index):

            self.n    = Natalia 
            self.data = self.n.config['plugins'][plugin_index]['data']
            self.check_config_integrity()

            ##############################################
            # END default, begin plugin
            ##############################################

            log.heading2('Adding member join hook to new_chat_member')
            self.n.dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, self.new_chat_member), group=priority_index)

            log.heading2('Adding member leave hook to left_chat_member')
            self.n.dp.add_handler(MessageHandler(Filters.status_update.left_chat_member, self.left_chat_member), group=priority_index)


        def new_chat_member(self, update, callback):
            """ Welcomes new chat member """
            
            pprint('New chat member %s ' % (__file__ ))
            pprint(update.__dict__)
            pprint(update.message.__dict__)
            pprint(update.message.new_chat_members[0].__dict__)

            try: 

                lenchatmembers = len(update.message.new_chat_members)
                user_id    = update.message.new_chat_members[lenchatmembers-1].id 
                message_id = update.message.message_id 
                chat_id    = update.message.chat.id
                chat_link  = update.message.chat.username 

                try:
                    log.print('Logging of joining of room... ')
                    self.n.add_room_join( message_id, chat_id, user_id )
                except Exception:
                    log.error('Unable to log join of room')

                if self.n.config['lockdown'] == True:

                    now = datetime.datetime.now()
                    rd = relativedelta(days=400)
                    perms = ChatPermissions(can_send_messages=False, can_send_media_messages=False, can_send_polls=False, can_send_other_messages=False, can_add_web_page_previews=False, can_change_info=False, can_invite_users=True, can_pin_messages=False)
                    self.n.bot.restrict_chat_member(chat_id, user_id, perms, until_date=(now + rd))        

                    self.n.bot.delete_message(chat_id=chat_id, message_id=message_id)

                    return 


                
                try:
                    name = update.message.new_chat_members[lenchatmembers-1].username
                    if name == None:
                        name = update.message.new_chat_members[lenchatmembers-1].first_name
                except Exception:
                    name =  update.message.new_chat_members[lenchatmembers-1].first_name
 
                # Bot was added to a group chat
                joiner_is_self = False 
                if name == self.n.config['bot_name']:
                    return 

                self.n.check_user_exists( user_id, name,  update.message.new_chat_members[lenchatmembers-1].username )

                # Is a valid room we have settings for 
                if chat_id not in self.n.config['rooms']:
                    log.error('New chat memeber in room '+str(chat_id)+' which is not in the rooms config')

                    # Get the chat info 
                    chat_info = self.n.bot.getChat(chat_id)

                    # Leave if setting set 
                    if self.n.config['leave_chat_if_no_rooms_setting'] == True:
                        log.error('Making bot leave chat '+chat_info.title )
                        self.n.bot.leaveChat(chat_id)

                    pprint(chat_info.__dict__)
                    return 
                
                # Assign a variable to the room data
                room_data = self.n.config['rooms'][chat_id]

                # Log that we have a new user joining the room 
                log.heading(str(name)+'('+str(user_id)+') joined '+room_data['chat_name']+', '+chat_link+', chat_id: '+str(chat_id))


                # Is a profile pic required ? 
                try : 
                    if room_data['profile_pic_required'] == True:
                        check_profile_pic = True
                except Exception:
                    check_profile_pic = False

                if check_profile_pic == True:
                    # Get the users profile pics
                    profile_pics = self.n.bot.getUserProfilePhotos(user_id=user_id)

                    # If no profile pic...
                    if profile_pics.total_count == 0:

                        # Log it
                        log.print(str(name)+' has no profile pic, restricting')

                        # Delete any previous messages
                        self.n.rooms_clear_last_self_msg(chat_id)

                        if room_data['welcome_users'] == True: 
                            # Tell them the profile pic is required
                            msg = update.message.reply_text(self.n.config['room_profile_pic_required_msg'].format(days=self.n.config['room_profile_pic_muting_days']))

                            # Store this reply message_id as the last one we should delete when msging in public chats 
                            if isinstance(msg.message_id, int):
                                self.n.config['rooms'][chat_id]['last_room_self_msg'] = msg.message_id

                        muting_days = self.n.config['room_profile_pic_muting_days']

                        # If a per room setting is longer duration than muting without profile pic duration, then use that instead
                        try: 
                            if room_data['restrict_new_users_days'] > self.n.config['room_profile_pic_muting_days']:
                                muting_days = room_data['restrict_new_users_days']
                        except Exception: 
                            pass 


                        now = datetime.datetime.now()
                        rd = relativedelta(days=muting_days)


                        self.n.update_user_room( user_id, chat_id, 'auto_restrict' )

                        # Retrict them
                        # restrict_chat_member(chat_id, user_id, permissions, until_date=None, timeout=None, **kwargs)
                        perms = ChatPermissions(can_send_messages=False, can_send_media_messages=False,
   can_send_polls=False, can_send_other_messages=False,
   can_add_web_page_previews=False, can_change_info=False,
   can_invite_users=True, can_pin_messages=False)
                        self.n.bot.restrict_chat_member(chat_id, user_id, perms, until_date=(now + rd))        

                        log.print('Restricting '+str(name)+' complete, end in '+str(muting_days)+' days at '+str(now+rd))
                        # end 
                        return True 


                # User has a profile pic: Check. 
                # Are we auto restricting new users ? 
                restrict = True 
                try : 
                    if 'restrict_new_users_days' in room_data:
                        # Log it
                        restrict = True

                except Exception:
                    restrict = False

                if restrict == True:

                    if room_data['restrict_new_users_days'] == False:
                        restrict = False

                if restrict == True:
                    
                    try:
                        if room_data['fast_unlock_with_captcha'] == True:
                            if self.n.users[user_id]['captcha_complete'] == 1:
                                restrict = False 
                    except Exception:
                        pass 

                if restrict == False:
                    self.n.update_user_room( user_id, chat_id, 'no_restrictions') 

                if restrict == True: 
                    now = datetime.datetime.now()
                    rd = relativedelta(days=room_data['restrict_new_users_days'])

                    # Restrict them 
                    self.n.update_user_room( user_id, chat_id, 'auto_restrict' )
                    
                    
                    log.print(room_data['chat_name']+' chat rules, restricting')
                    perms = ChatPermissions(
                            can_send_messages=False, 
                            can_send_media_messages=False,
                            can_send_polls=False, 
                            can_send_other_messages=False,
                            can_add_web_page_previews=False, 
                            can_change_info=False,
                            can_invite_users=True, 
                            can_pin_messages=False
                        )
                    try: 
                        self.n.bot.restrict_chat_member(chat_id, user_id, perms, until_date=(now + rd))        
                        log.print('Restricting '+str(name)+' complete, end in '+str(room_data['restrict_new_users_days'])+' days at '+str(now+rd))
                    except Exception:
                        log.error('Unable to restrict user %s in %s, do not have permissions to restrict' % (name, room_data['chat_name']))

                try: 
                    if room_data['welcome_users'] == True: 
                        welcome = True
                except Exception:
                    welcome = False

                if welcome == True: 

                    welcome_msg = random.choice(self.data['welcome'])
                    
                    if 'custom_welcome_msg' in room_data: 
                        welcome_msg = room_data['custom_welcome_msg']

                    # Delete any previous messages
                    self.n.rooms_clear_last_self_msg(chat_id)

                    # Reply with the welcome message
                    name = helpers.escape_markdown(name)
                    msg = welcome_msg.format(name=name)
                    msg = update.message.reply_text(msg)

                    # Store this reply message_id as the last one we should delete when msging in public chats 
                    if isinstance(msg.message_id, int):
                        self.n.config['rooms'][chat_id]['last_room_self_msg'] = msg.message_id




            except Exception as e:
                    log.error(traceback.format_exc())



            # if (chat_id == WP_ROOM) or (chat_id == SP_ROOM) or (chat_id == WP_WOMENS):
            #   # Check user has a profile pic.. 

            #   timestamp = datetime.datetime.utcnow()

            #   info = { 'user_id': user_id, 'chat_id': chat_id, 'timestamp': timestamp }
            #   db.room_joins.insert(info)





        def left_chat_member(self, update, callback):

            # print('User left chat..')
            # pprint(update.__dict__)
            # pprint(update.message.__dict__)
            # pprint(update.message.left_chat_member.__dict__)
            try: 

                user_id    = update.message.left_chat_member.id
                chat_id    = update.message.chat.id 
                chat_name  = update.message.chat.title 
                chat_link  = update.message.chat.username 

                try: 
                    name       = update.message.left_chat_member.username
                except Exception:
                    name = update.message.left_chat_member.first_name

                self.n.check_user_exists( user_id, name, update.message.left_chat_member.username )
                self.n.del_user_room( user_id, chat_id )

                # Is a valid room we have settings for 
                if chat_id in self.n.config['rooms']:

                    # Assign a variable to the room data
                    room_data = self.n.config['rooms'][chat_id]

                    # Log that we have a new user joining the room 
                    log.print(str(name)+' left  chat: '+room_data['chat_name']+', @'+chat_link+', chat_id: '+str(chat_id))

                    # Delete any previous messages
                    self.n.rooms_clear_last_self_msg(chat_id)
                    
                    try: 
                        if room_data['goodbye_users'] == True: 
                            bye = True
                    except Exception:
                        bye = False

                    if bye == True: 
                        bye_msg = random.choice(self.data['goodbye'])
 
                        if 'custom_bye_msg' in room_data :
                            bye_msg = room_data['custom_bye_msg']

                        msg = bye_msg.format(name=helpers.escape_markdown(name))

                        msg = self.n.bot.sendMessage(chat_id=chat_id, text=msg,parse_mode="Markdown",disable_web_page_preview=1)
                        if isinstance(msg.message_id, int):
                            self.n.config['rooms'][chat_id]['last_room_self_msg'] = msg.message_id


                # Else, receiving data for a room with no config
                else: 
                    log.error(str(name)+' left  chat: '+chat_name+', @'+chat_link+', chat_id: '+str(chat_id))



            except Exception as e:
                log.error(traceback.format_exc())


                # pprint(update.message.chat.__dict__)
                # pprint(update.message.chat.__dict__)
                # pprint(update.message.from_user.__dict__)
                # pprint(update.message.left_chat_member.__dict__)


        def check_config_integrity(self):

            log.print('checking welcome_goodbye plugin config')
            check       = ['welcome','goodbye']
            errors_list = []
            errors      = 0

            for check_type in check: 
                if check_type not in self.data:
                    errors += 1
                    errors_list.append('Missing '+check_type+' messages in config')

                elif type(self.data[check_type]) is not list:
                    errors += 1
                    errors_list.append('No '+check_type+' messages found')

                else:
                    if (self.data[check_type][0] == ''):
                        errors += 1
                        errors_list.append('First '+check_type+' message is empty')

                self.n.check_for_errors(errors, errors_list)



def run(Natalia, plugin_index, priority_index):

    return Welcome_Goodbye(Natalia, plugin_index, priority_index) 
