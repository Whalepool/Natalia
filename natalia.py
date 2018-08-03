#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# A Simple way to send a message to telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler
from telegram import MessageEntity, TelegramObject, ChatAction
from pprint import pprint
from functools import wraps
from future.builtins import bytes
from pymongo import MongoClient
from pathlib import Path
import numpy as np
import argparse
import logging
import telegram
import sys
import json
import random
import datetime
from dateutil.relativedelta import relativedelta
import re 
import os
import sys
import yaml
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from PIL import Image

# For plotting messages / price charts
import pandas as pd 

import requests

import matplotlib 
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle, Patch
from matplotlib.finance import candlestick_ohlc

import talib as ta

PATH = os.path.dirname(os.path.abspath(__file__))

"""
# Configure Logging
"""
FORMAT = '%(asctime)s -- %(levelname)s -- %(module)s %(lineno)d -- %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger('root')
logger.info("Running "+sys.argv[0])


"""
# Mongodb 
"""
client  = MongoClient('mongodb://localhost:27017')
db      = client.natalia_tg_bot


"""
#	Load the config file
#	Set the Botname / Token
"""
config_file = PATH+'/config.yaml'
my_file     = Path(config_file)
if my_file.is_file():
	with open(config_file) as fp:
	    config = yaml.load(fp)
else:
	pprint('config.yaml file does not exists. Please make from config.sample.yaml file')
	sys.exit()


BOTNAME                     = config['NATALIA_BOT_USERNAME']
TELEGRAM_BOT_TOKEN          = config['NATALIA_BOT_TOKEN']
FORWARD_PRIVATE_MESSAGES_TO = config['BOT_OWNER_ID'] 
ADMINS                      = config['ADMINS']

EXTRA_STOPWORDS    = config['WORDCLOUD_STOPWORDS']
FORWARD_URLS       = r""+config['FORWARD_URLS']
SHILL_DETECTOR     = r""+config['SHILL_DETECTOR']
COUNTER_SHILL      = []

for s in config['COUNTER_SHILL']:
	COUNTER_SHILL.append({
	'title': s['title'],
	'regex': r""+s['match'],
	'link' : s['link']
	})

MESSAGES = {}
MESSAGES['welcome']         = config['MESSAGES']['welcome']
MESSAGES['welcomewomen']    = config['MESSAGES']['welcome_special']
MESSAGES['goodbye']         = config['MESSAGES']['goodbye']
MESSAGES['pmme']            = config['MESSAGES']['pmme']
MESSAGES['start']           = config['MESSAGES']['start']
MESSAGES['admin_start']     = config['MESSAGES']['admin_start']
MESSAGES['about']           = config['MESSAGES']['about']
MESSAGES['rules']           = config['MESSAGES']['rules']
MESSAGES['teamspeak']       = config['MESSAGES']['teamspeak']
MESSAGES['telegram']        = config['MESSAGES']['telegram']
MESSAGES['livestream']      = config['MESSAGES']['livestream']
MESSAGES['exchanges']       = config['MESSAGES']['exchanges']
MESSAGES['shill']           = config['MESSAGES']['shill']  
MESSAGES['teamspeakbadges'] = config['MESSAGES']['teamspeakbadges']
MESSAGES['fomobot']         = config['MESSAGES']['fomobot']
MESSAGES['donate']          = config['MESSAGES']['donate']

ADMINS_JSON                 = config['MESSAGES']['admins_json']



# Rooms 
WP_ROOM     = -1001012147388      # Whalepool
SP_ROOM     = -1001120581521      # Shitpool
WP_ADMIN    = -238862165          # Whalepool Admin
MH_ROOM     = -1001213548615      # Master Holder room
TEST_ROOM   = -1001223115449     # Test room
WP_WOMENS   = -1001248205448      # Whalepool Womens
WP_FEED     = "@whalepoolbtcfeed" # Whalepool Feed
SP_FEED     = "@shitcoincharts" # shitpool feed

ROOM_ID_TO_NAME = {
	WP_ROOM : 'Whalepool',
	SP_ROOM : 'Shitpool',
	WP_ADMIN: 'Whalepool Mod room',
	MH_ROOM : 'Whalepool Trading Dojo',
	TEST_ROOM: 'Test room',
	WP_WOMENS : 'Whalepool Womens',
	WP_FEED : 'Whalepool Feed channel',
	SP_FEED : 'Shitpool Feed channel'
}

# Rooms where chat/gifs/etc is logged for stats etc 
LOG_ROOMS = [ WP_ROOM, SP_ROOM, TEST_ROOM ]


# Storing last 'welcome' message ids 
PRIOR_WELCOME_MESSAGE_ID = {
	WP_ROOM   : 0,
	SP_ROOM   : 0,
	MH_ROOM   : 0,
	TEST_ROOM : 0,
	WP_WOMENS : 0
}

# Storing last 'removal' of uncompress images, message ids
LASTUNCOMPRESSED_IMAGES = { 
	WP_ROOM   : 0,
	SP_ROOM   : 0,
	MH_ROOM   : 0,
	TEST_ROOM : 0,
	WP_WOMENS : 0
}

# Hashtags that forward messages to specific channels
forward_hashtags = {
	'#communityfund' : WP_FEED,
	'#community' : WP_FEED
}





#################################
# Begin bot.. 

bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

# Bot error handler
def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

# Restrict bot functions to admins
def restricted(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in ADMINS:
            print("Unauthorized access denied for {}.".format(user_id))
            return
        return func(bot, update, *args, **kwargs)
    return wrapped




#################################
#			UTILS	

# Resolve message data to a readable name 	 		
def get_name(user):
        try:
            name = user.first_name
        except (NameError, AttributeError):
            try:
                name = user.username
            except (NameError, AttributeError):
                logger.info("No username or first name.. wtf")
                return	""
        return name



#################################
#		BEGIN BOT COMMANDS 		

# Returns the user their user id 
def getid(bot, update):
	pprint(update.message.chat.__dict__, indent=4)
	update.message.reply_text(str(update.message.chat.first_name)+" :: "+str(update.message.chat.id))

# Welcome message 
def start(bot, update):

	user_id = update.message.from_user.id 
	chat_id = update.message.chat.id
	message_id = update.message.message_id
	user_id = update.message.from_user.id 
	name = get_name(update.message.from_user)
	logger.info("/start - "+name)

	pprint(update.message.chat.type)

	if (update.message.chat.type == 'group') or (update.message.chat.type == 'supergroup'):
		msg = random.choice(MESSAGES['pmme']) % (name)
		bot.sendMessage(chat_id=chat_id,text=msg,reply_to_message_id=message_id, parse_mode="Markdown",disable_web_page_preview=1) 
	else:
		msg = MESSAGES['rules']

		timestamp = datetime.datetime.utcnow()
		info = { 'user_id': user_id, 'request': 'start', 'timestamp': timestamp }
		db.pm_requests.insert(info)

		msg = bot.sendMessage(chat_id=chat_id, text=(MESSAGES['start'] % name),parse_mode="Markdown",disable_web_page_preview=1)

		if user_id in ADMINS:
			msg = bot.sendMessage(chat_id=chat_id, text=(MESSAGES['admin_start'] % name),parse_mode="Markdown",disable_web_page_preview=1)



def about(bot, update):

	user_id = update.message.from_user.id 
	chat_id = update.message.chat.id
	message_id = update.message.message_id
	name = get_name(update.message.from_user)
	logger.info("/about - "+name)

	if (update.message.chat.type == 'group') or (update.message.chat.type == 'supergroup'):
		msg = random.choice(MESSAGES['pmme']) % (name)
		bot.sendMessage(chat_id=chat_id,text=msg,reply_to_message_id=message_id, parse_mode="Markdown",disable_web_page_preview=1) 
	else:
		msg = MESSAGES['about']


		timestamp = datetime.datetime.utcnow()
		info = { 'user_id': user_id, 'request': 'about', 'timestamp': timestamp }
		db.pm_requests.insert(info)

		bot.sendMessage(chat_id=chat_id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 


def rules(bot, update):

	user_id = update.message.from_user.id 
	chat_id = update.message.chat.id
	message_id = update.message.message_id
	name = get_name(update.message.from_user)
	logger.info("/rules - "+name)

	if (update.message.chat.type == 'group') or (update.message.chat.type == 'supergroup'):
		msg = random.choice(MESSAGES['pmme']) % (name)
		bot.sendMessage(chat_id=chat_id,text=msg,reply_to_message_id=message_id, parse_mode="Markdown",disable_web_page_preview=1) 
	else:
		msg = MESSAGES['rules']

		timestamp = datetime.datetime.utcnow()
		info = { 'user_id': user_id, 'request': 'rules', 'timestamp': timestamp }
		db.pm_requests.insert(info)

		bot.sendMessage(chat_id=chat_id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 


def admins(bot, update):

	user_id = update.message.from_user.id 
	chat_id = update.message.chat.id
	message_id = update.message.message_id
	name = get_name(update.message.from_user)
	logger.info("/admins - "+name)

	if (update.message.chat.type == 'group') or (update.message.chat.type == 'supergroup'):
		msg = random.choice(MESSAGES['pmme']) % (name)
		bot.sendMessage(chat_id=chat_id,text=msg,reply_to_message_id=message_id, parse_mode="Markdown",disable_web_page_preview=1) 
	else:
		msg = "*Whalepool Admins*\n\n"
		keys = list(ADMINS_JSON.keys())
		random.shuffle(keys)
		for k in keys: 
			msg += ""+k+"\n"
			msg += ADMINS_JSON[k]['adminOf']+"\n"
			msg += "_"+ADMINS_JSON[k]['about']+"_"
			msg += "\n\n"
		msg += "/start - to go back to home"

		timestamp = datetime.datetime.utcnow()
		info = { 'user_id': user_id, 'request': 'admins', 'timestamp': timestamp }
		db.pm_requests.insert(info)

		bot.sendMessage(chat_id=chat_id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 


def teamspeak(bot, update):

	user_id = update.message.from_user.id 
	chat_id = update.message.chat.id
	message_id = update.message.message_id
	name = get_name(update.message.from_user)
	logger.info("/teamspeak - "+name)

	if (update.message.chat.type == 'group') or (update.message.chat.type == 'supergroup'):
		msg = random.choice(MESSAGES['pmme']) % (name)
		bot.sendMessage(chat_id=chat_id,text=msg,reply_to_message_id=message_id, parse_mode="Markdown",disable_web_page_preview=1) 
	else:
		msg = MESSAGES['teamspeak']

		timestamp = datetime.datetime.utcnow()
		info = { 'user_id': user_id, 'request': 'teamspeak', 'timestamp': timestamp }
		db.pm_requests.insert(info)

		bot.sendSticker(chat_id=chat_id, sticker="CAADBAADqgIAAndCvAiTIPeFFHKWJQI", disable_notification=False)
		bot.sendMessage(chat_id=chat_id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 


def teamspeakbadges(bot, update):

	user_id = update.message.from_user.id 
	chat_id = update.message.chat.id
	message_id = update.message.message_id
	name = get_name(update.message.from_user)
	logger.info("/teamspeakbadges - "+name)

	if (update.message.chat.type == 'group') or (update.message.chat.type == 'supergroup'):
		msg = random.choice(MESSAGES['pmme']) % (name)
		bot.sendMessage(chat_id=chat_id,text=msg,reply_to_message_id=message_id, parse_mode="Markdown",disable_web_page_preview=1) 
	else:
		msg = MESSAGES['teamspeakbadges']

		timestamp = datetime.datetime.utcnow()
		info = { 'user_id': user_id, 'request': 'teamspeakbadges', 'timestamp': timestamp }
		db.pm_requests.insert(info)

		bot.sendMessage(chat_id=chat_id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 

		
def telegram(bot, update):

	user_id = update.message.from_user.id 
	chat_id = update.message.chat.id
	message_id = update.message.message_id
	name = get_name(update.message.from_user)
	logger.info("/telegram - "+name)

	if (update.message.chat.type == 'group') or (update.message.chat.type == 'supergroup'):
		msg = random.choice(MESSAGES['pmme']) % (name)
		bot.sendMessage(chat_id=chat_id,text=msg,reply_to_message_id=message_id, parse_mode="Markdown",disable_web_page_preview=1) 
	else:
		msg = MESSAGES['telegram']

		timestamp = datetime.datetime.utcnow()
		info = { 'user_id': user_id, 'request': 'telegram', 'timestamp': timestamp }
		db.pm_requests.insert(info)

		bot.sendMessage(chat_id=chat_id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 


def livestream(bot, update):

	user_id = update.message.from_user.id 
	chat_id = update.message.chat.id
	message_id = update.message.message_id
	name = get_name(update.message.from_user)
	logger.info("/livestream - "+name)

	if (update.message.chat.type == 'group') or (update.message.chat.type == 'supergroup'):
		msg = random.choice(MESSAGES['pmme']) % (name)
		bot.sendMessage(chat_id=chat_id,text=msg,reply_to_message_id=message_id, parse_mode="Markdown",disable_web_page_preview=1) 
	else:
		msg = MESSAGES['livestream']

		timestamp = datetime.datetime.utcnow()
		info = { 'user_id': user_id, 'request': 'livestream', 'timestamp': timestamp }
		db.pm_requests.insert(info)

		bot.sendSticker(chat_id=chat_id, sticker="CAADBAADcwIAAndCvAgUN488HGNlggI", disable_notification=False)
		bot.sendMessage(chat_id=chat_id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 


def fomobot(bot, update):

	user_id = update.message.from_user.id 
	chat_id = update.message.chat.id
	message_id = update.message.message_id
	name = get_name(update.message.from_user)
	logger.info("/fomobot - "+name)

	if (update.message.chat.type == 'group') or (update.message.chat.type == 'supergroup'):
		msg = random.choice(MESSAGES['pmme']) % (name)
		bot.sendMessage(chat_id=chat_id,text=msg,reply_to_message_id=message_id, parse_mode="Markdown",disable_web_page_preview=1) 
	else:
		msg = MESSAGES['fomobot']

		timestamp = datetime.datetime.utcnow()
		info = { 'user_id': user_id, 'request': 'fomobot', 'timestamp': timestamp }
		db.pm_requests.insert(info)

		bot.sendMessage(chat_id=chat_id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 


def exchanges(bot, update):

	user_id = update.message.from_user.id 
	chat_id = update.message.chat.id
	message_id = update.message.message_id
	name = get_name(update.message.from_user)
	logger.info("/exchanges - "+name)

	if (update.message.chat.type == 'group') or (update.message.chat.type == 'supergroup'):
		msg = random.choice(MESSAGES['pmme']) % (name)
		bot.sendMessage(chat_id=chat_id,text=msg,reply_to_message_id=message_id, parse_mode="Markdown",disable_web_page_preview=1) 
	else:
		msg = MESSAGES['exchanges']

		timestamp = datetime.datetime.utcnow()
		info = { 'user_id': user_id, 'request': 'exchanges', 'timestamp': timestamp }
		db.pm_requests.insert(info)

		bot.sendMessage(chat_id=chat_id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 
		# bot.forwardMessage(chat_id=WP_ADMIN, from_chat_id=chat_id, message_id=message_id)


def donation(bot, update):

	user_id = update.message.from_user.id 
	chat_id = update.message.chat.id
	message_id = update.message.message_id
	name = get_name(update.message.from_user)
	logger.info("/donation - "+name)

	if (update.message.chat.type == 'group') or (update.message.chat.type == 'supergroup'):
		msg = random.choice(MESSAGES['pmme']) % (name)
		bot.sendMessage(chat_id=chat_id,text=msg,reply_to_message_id=message_id, parse_mode="Markdown",disable_web_page_preview=1) 
	else:

		timestamp = datetime.datetime.utcnow()
		info = { 'user_id': user_id, 'request': 'donation', 'timestamp': timestamp }
		db.pm_requests.insert(info)

		bot.sendPhoto(chat_id=chat_id, photo="AgADBAADlasxG4uhCVPAkVD5G4AaXgtKXhkABL8N5jNhPaj1-n8CAAEC",caption="Donations by bitcoin to: 175oRbKiLtdY7RVC8hSX7KD69WQs8PcRJA")


####################################################
# ADMIN FUNCTIONS

@restricted
def topstickers(bot,update):	

	user_id = update.message.from_user.id 
	chat_id = update.message.chat.id

	start = datetime.datetime.today().replace(hour=0,minute=0,second=0)
	start = start - relativedelta(days=3)

	pipe = [ 
		{ "$match": { 'timestamp': {'$gt': start } } }, 
		{ "$group": { "_id": "$sticker_id", "total": { "$sum": 1 }  } }, 
		{ "$sort": { "total": -1 } }, 
		{ "$limit": 3 }   
	]
	gifs = list(db.natalia_stickers.aggregate(pipe))

	bot.sendMessage(chat_id=update.message.chat_id, text="Posting... sometimes this can cause the telegram api to 'time out' ? so won't complete posting but trying anyway.." )
	bot.sendMessage(chat_id=WP_ROOM, text="Whalepool most popular 3 stickers in the last 3 days are..." )
	for g in gifs:
		pprint(g)
		bot.sendMessage(chat_id=WP_ROOM, text="with "+str(g['total'])+" posts..")
		bot.sendSticker(chat_id=WP_ROOM, sticker=g['_id'], disable_notification=False)
		time.sleep(5)
	bot.sendMessage(chat_id=update.message.chat_id, text="message has been posted to "+ROOM_ID_TO_NAME[WP_ROOM] )




@restricted
def topgif(bot,update):

	chat_id = update.message.chat.id

	pipe = [ { "$group": { "_id": "$file_id", "total": { "$sum": 1 }  } }, { "$sort": { "total": -1 } }, { "$limit": 5 }   ]
	gifs = list(db.natalia_gifs.aggregate(pipe))

	bot.sendMessage(chat_id=WP_ROOM, text="Whalepool most popular gif ever with "+str(gifs[0]['total'])+" posts is..." )
	bot.sendSticker(chat_id=WP_ROOM, sticker=gifs[0]['_id'], disable_notification=False)
	bot.sendMessage(chat_id=chat_id, text="message has been posted to "+ROOM_ID_TO_NAME[WP_ROOM] )


@restricted
def topgifposters(bot, update):


	chat_id = update.message.chat.id

	pipe = [ { "$group": { "_id": "$user_id", "total": { "$sum": 1 }  } }, { "$sort": { "total": -1 } }, { "$limit": 5 }   ]
	users = list(db.natalia_gifs.aggregate(pipe))

	msg = "I'm naming and shaming the top 5 gif posters in "+ROOM_ID_TO_NAME[WP_ROOM]
	for i,u in enumerate(users):


		user = list(db.users.find({ 'user_id': u['_id'] }))
		if len(user) > 0:
			user = user[0]
			msg += "\n#"+str(i+1)+" - "+user['name']+" with "+str(u['total'])+" gifs"



	msg = bot.sendMessage(chat_id=WP_ROOM, text=msg )
	bot.forwardMessage(chat_id=chat_id, from_chat_id=WP_ROOM, message_id=msg.message_id)
	bot.sendMessage(chat_id=chat_id, text="message has been posted to "+ROOM_ID_TO_NAME[WP_ROOM] )



@restricted
def todayinwords(bot, update):

	chat_id = update.message.chat.id

	logger.info("Today in words..")
	logger.info("Fetching from db...")

	start = datetime.datetime.today().replace(hour=0,minute=0,second=0)
	pipe  = { '_id': 0, 'message': 1 }
	msgs  = list(db.natalia_textmessages.find({ 'timestamp': {'$gt': start } }, pipe ))

	words = []
	for w in msgs:
		results = re.findall(r"(.*(?=:)): (.*)", w['message'])[0]
		words.append(results[1].strip())

	extra_stopwords = EXTRA_STOPWORDS
	for e in extra_stopwords:
		STOPWORDS.add(e)

	stopwords = set(STOPWORDS)


	logger.info("Building comments pic...")

	# Happening today
	wc = WordCloud(background_color="white", max_words=2000, stopwords=stopwords, relative_scaling=0.2,scale=3)
	# generate word cloud
	wc.generate(' '.join(words))
	# store to file
	PATH_WORDCLOUD = PATH+"talkingabout_wordcloud.png"
	wc.to_file(PATH_WORDCLOUD)

	msg = bot.sendPhoto(chat_id=WP_ROOM, photo=open(PATH_WORDCLOUD,'rb'), caption="Today in a picture" )
	bot.sendMessage(chat_id=chat_id, text="Posted today in pictures to "+ROOM_ID_TO_NAME[WP_ROOM] )

	os.remove(PATH_WORDCLOUD)


@restricted
def todaysusers(bot, update):

	chat_id = update.message.chat.id

	bot.sendMessage(chat_id=chat_id, text="Okay gimme a second for this one.. it takes some resources.." )
	logger.info("Today in words..")
	logger.info("Fetching from db...")

	start = datetime.datetime.today().replace(hour=0,minute=0,second=0)
	pipe  = { '_id': 0, 'message': 1 }
	msgs  = list(db.natalia_textmessages.find({ 'timestamp': {'$gt': start } }, pipe ))

	usernames = []
	for w in msgs:
		results = re.findall(r"(.*(?=:)): (.*)", w['message'])[0]
		usernames.append(results[0].strip())

	extra_stopwords = EXTRA_STOPWORDS
	for e in extra_stopwords:
		STOPWORDS.add(e)

	stopwords = set(STOPWORDS)

	logger.info("Building usernames pic...")
	PATH_MASK      = PATH+"media/wp_background_mask2.png"
	PATH_BG        = PATH+"media/wp_background.png"
	PATH_USERNAMES = PATH+"telegram-usernames.png"

	# Usernames
	d = os.path.dirname('__file__')

	mask = np.array(Image.open(PATH_MASK))

	wc = WordCloud(background_color=None, max_words=2000,mask=mask,colormap='BuPu',
	               stopwords=stopwords,mode="RGBA", width=800, height=400)
	wc.generate(' '.join(usernames))
	wc.to_file(PATH_USERNAMES)

	layer1 = Image.open(PATH_BG).convert("RGBA")
	layer2 = Image.open(PATH_USERNAMES).convert("RGBA")

	Image.alpha_composite(layer1, layer2).save(PATH_USERNAMES)

	msg = bot.sendPhoto(chat_id=WP_ROOM, photo=open("telegram-usernames.png",'rb'), caption="Todays Users" )
	bot.sendMessage(chat_id=chat_id, text="Posted today in pictures to "+ROOM_ID_TO_NAME[WP_ROOM] )

	os.remove(PATH_USERNAMES)


@restricted 
def promotets(bot, update):

	pprint('promotets...')

	chat_id = update.message.chat_id
	name = get_name(update.message.from_user)
	fmsg = re.findall( r"\"(.*?)\"", update.message.text)

	if len(fmsg) > 0:

		# rooms = [WP_ROOM]
		rooms = [WP_ROOM, SP_ROOM, MH_ROOM, WP_FEED, SP_FEED]

		for r in rooms:

			message = fmsg[0]
			bot.sendSticker(chat_id=r, sticker="CAADBAADcwIAAndCvAgUN488HGNlggI", disable_notification=False)
			msg = bot.sendMessage(chat_id=r, parse_mode="Markdown", text=fmsg[0]+"\n-------------------\n*/announcement from "+name+"*" )


			if r in [WP_ROOM, SP_ROOM, MH_ROOM]: 
				bot.pin_chat_message(r, msg.message_id, disable_notification=True)

			bot.sendMessage(chat_id=r, parse_mode="Markdown", text="Message me ("+BOTNAME.replace('_','\_')+") - to see details on how to connect to [teamspeak](https://whalepool.io/connect/teamspeak) also listen in to the listream here: livestream.whalepool.io", disable_web_page_preview=True )
			bot.sendMessage(chat_id=chat_id, parse_mode="Markdown", text="Broadcast sent to "+ROOM_ID_TO_NAME[r])

			

	else:
		bot.sendMessage(chat_id=chat_id, text="Please incldue a message in quotes to spam/shill the teamspeak message" )

	 
@restricted
def shill(bot, update):

	chat_id = update.message.chat_id
	name = get_name(update.message.from_user)

	bot.sendMessage(chat_id=WP_ADMIN, parse_mode="Markdown", text=name+" just shilled")

	rooms = [WP_ROOM, SP_ROOM, WP_FEED, SP_FEED]

	for r in rooms:
		bot.sendMessage(chat_id=r, parse_mode="Markdown", text=MESSAGES['shill'],disable_web_page_preview=1)
		bot.sendMessage(chat_id=chat_id, parse_mode="Markdown", text="Shilled in "+ROOM_ID_TO_NAME[r])
	


@restricted
def commandstats(bot, update):
	chat_id = update.message.chat_id
	start = datetime.datetime.today().replace(day=1,hour=0,minute=0,second=0)
	# start = start - relativedelta(days=30)

	pipe = [ 
		{ "$match": { 'timestamp': {'$gt': start } } }, 
		{ "$group": { 
			"_id": { 
				"year" : { "$year" : "$timestamp" },        
				"month" : { "$month" : "$timestamp" },        
				"day" : { "$dayOfMonth" : "$timestamp" },
				"request": "$request"
			},
			"total": { "$sum": 1 }  
			} 
		}, 
		{ "$sort": { "total": -1  } }, 
		# { "$limit": 3 }   
	]
	res = list(db.pm_requests.aggregate(pipe))

	output = {}
	totals = {}

	for r in res: 

		key = r['_id']['day']
		if not(key in output):
			output[key] = {}

		request = r['_id']['request']
		if not(request in output[key]):
			output[key][r['_id']['request']] = 0 

		if not(request in totals):
			totals[request] = 0

		output[key][r['_id']['request']] += r['total']
		totals[request] += r['total']


	reply = "*Natalia requests since the start of the month...*\n"
	for day in sorted(output.keys()):
		reply += "--------------------\n"
		reply += "*"+str(day)+"*\n"

		for request, count in output[day].items():
			reply += request+" - "+str(count)+"\n"

			
	reply += "--------------------\n"
	reply += "*Totals*\n"
	for request in totals:
		reply += request+" - "+str(totals[request])+"\n"


	bot.sendMessage(chat_id=chat_id, text=reply, parse_mode="Markdown" )


@restricted 
def joinstats(bot,update):

	chat_id = update.message.chat_id
	start = datetime.datetime.today().replace(day=1,hour=0,minute=0,second=0)
	# start = start - relativedelta(days=30)

	pipe = [ 
		{ "$match": { 'timestamp': {'$gt': start } } }, 
		{ "$group": { 
			"_id": {     
				"day" : { "$dayOfMonth" : "$timestamp" },
				"chat_id": "$chat_id"
			},
			"total": { "$sum": 1 }  
			} 
		}, 
		{ "$sort": { "total": -1  } }, 
		# { "$limit": 3 }   
	]
	res = list(db.room_joins.aggregate(pipe))

	output = {}
	totals = {}

	for r in res: 

		key = r['_id']['day']
		if not(key in output):
			output[key] = {}

		roomid = r['_id']['chat_id']
		if not(roomid in output[key]):
			output[key][roomid] = 0 

		if not(roomid in totals):
			totals[roomid] = 0

		output[key][roomid] += r['total']
		totals[roomid] += r['total']



	reply = "*Channel Joins since the start of the month...*\n"
	for day in sorted(output.keys()):
		reply += "--------------------\n"
		reply += "*"+str(day)+"*\n"

		for room, count in output[day].items():
			reply += ROOM_ID_TO_NAME[room]+" - "+str(count)+"\n"


	reply += "--------------------\n"
	reply += "*Totals*\n"
	for roomid in totals:
		reply += ROOM_ID_TO_NAME[roomid]+" - "+str(totals[roomid])+"\n"


	bot.sendMessage(chat_id=chat_id, text=reply, parse_mode="Markdown" )


def fooCandlestick(ax, quotes, width=0.029, colorup='#FFA500', colordown='#222', alpha=1.0):
	OFFSET = width/2.0
	lines = []
	boxes = []

	for q in quotes:

		timestamp, op, hi, lo, close = q[:5]
		box_h = max(op, close)
		box_l = min(op, close)
		height = box_h - box_l

		if close>=op:
			color = '#3fd624'
		else:
			color = '#e83e2c'

		vline_lo = Line2D( xdata=(timestamp, timestamp), ydata=(lo, box_l), color = 'k', linewidth=0.5, antialiased=True, zorder=10 )
		vline_hi = Line2D( xdata=(timestamp, timestamp), ydata=(box_h, hi), color = 'k', linewidth=0.5, antialiased=True, zorder=10 )
		rect = Rectangle( xy = (timestamp-OFFSET, box_l), width = width, height = height, facecolor = color, edgecolor = color, zorder=10)
		rect.set_alpha(alpha)
		lines.append(vline_lo)
		lines.append(vline_hi)
		boxes.append(rect)
		ax.add_line(vline_lo)
		ax.add_line(vline_hi)
		ax.add_patch(rect)

	ax.autoscale_view()

	return lines, boxes

# Special function for testing purposes 
@restricted
def whalepooloverprice(bot, update):
	user_id = update.message.from_user.id 
	chat_id = update.message.chat_id


	bot.sendMessage(chat_id=61697695, text="Processing data" )

	
	# Room only
	mongo_match = { "$match": { 'chat_id': WP_ROOM } }


	do = 'hourly'

	if do == 'daily': 
		bar_width = 0.864
		api_timeframe = '1D'
		date_group_format = "%Y-%m-%d"

	if do == 'hourly': 
		bar_width         = 0.029
		api_timeframe     = '1h'
		date_group_format = "%Y-%m-%dT%H"



	# Get the candles
	url = 'https://api.bitfinex.com/v2/candles/trade:'+api_timeframe+':tBTCUSD/hist?limit=200'
	request = json.loads(requests.get(url).text)

	candles = pd.read_json(json.dumps(request))
	candles.rename(columns={0:'date', 1:'open', 2:'close', 3:'high', 4:'low', 5:'volume'}, inplace=True)
	candles['date'] = pd.to_datetime( candles['date'], unit='ms' )
	candles.set_index(candles['date'], inplace=True)
	candles.sort_index(inplace=True)

	first_candlestick_date = candles.index[0].to_pydatetime()

	del candles['date']
	candles = candles.reset_index()[['date','open','high','low','close','volume']]
	candles['date'] = candles['date'].map(mdates.date2num)


	# Users joins
	pipe =  [
	  mongo_match,
	  { "$group": {
			"_id":    { "$dateToString": { "format": date_group_format, "date": "$timestamp" } },
			"count":  { "$sum": 1 }
		}	
	  },
	]
	rows = list(db.room_joins.aggregate(pipe))

	userjoins = pd.DataFrame(rows)
	userjoins['date'] = pd.to_datetime( userjoins['_id'], format=date_group_format)
	# msgs['date'] = pd.to_datetime( msgs['_id'], format='%Y-%m-%d')
	del userjoins['_id']
	userjoins.set_index(userjoins['date'], inplace=True)
	userjoins.sort_index(inplace=True)

	userjoins['date'] = userjoins['date'].map(mdates.date2num)
	userjoins = userjoins.loc[first_candlestick_date:]



	# Get the messages
	pipe =  [
	  mongo_match,
	  { "$group": {
			"_id":    { "$dateToString": { "format": date_group_format, "date": "$timestamp" } },
			"count":  { "$sum": 1 }
		}	
	  },
	]
	rows = list(db.natalia_textmessages.aggregate(pipe))

	msgs = pd.DataFrame(rows)
	msgs['date'] = pd.to_datetime( msgs['_id'], format=date_group_format)
	# msgs['date'] = pd.to_datetime( msgs['_id'], format='%Y-%m-%d')
	del msgs['_id']
	msgs.set_index(msgs['date'], inplace=True)
	msgs.sort_index(inplace=True)

	msgs['date'] = msgs['date'].map(mdates.date2num)
	msgs = msgs.loc[first_candlestick_date:]


	# Stickers
	pipe =  [
	  mongo_match,
	  { "$group": {
			"_id":    { "$dateToString": { "format": date_group_format, "date": "$timestamp" } },
			"count":  { "$sum": 1 }
		}	
	  },
	]
	rows = list(db.natalia_stickers.aggregate(pipe))

	gifs = pd.DataFrame(rows)
	gifs['date'] = pd.to_datetime( gifs['_id'], format='%Y-%m-%dT%H')
	# msgs['date'] = pd.to_datetime( msgs['_id'], format='%Y-%m-%d')
	del gifs['_id']
	gifs.set_index(gifs['date'], inplace=True)
	gifs.sort_index(inplace=True)
	gifs['date'] = gifs['date'].map(mdates.date2num)
	gifs = gifs.loc[first_candlestick_date:]




	# Enable a Grid
	plt.rc('axes', grid=True)
	# Set Grid preferences 
	plt.rc('grid', color='0.75', linestyle='-', linewidth=0.5)

	# Create a figure, 16 inches by 12 inches
	fig = plt.figure(facecolor='white', figsize=(22, 12), dpi=100)

	# Draw 3 rectangles
	# left, bottom, width, height
	left, width = 0.1, 1
	rect1 = [left, 0.7, width, 0.5]
	rect2 = [left, 0.5, width, 0.2]
	rect3 = [left, 0.3, width, 0.2]
	rect4 = [left, 0.1, width, 0.2]

	ax1 = fig.add_axes(rect1, facecolor='#f6f6f6')  
	ax2 = fig.add_axes(rect2, facecolor='#f6f6f6', sharex=ax1)
	ax3 = fig.add_axes(rect3, facecolor='#f6f6f6', sharex=ax1)
	ax4 = fig.add_axes(rect4, facecolor='#f6f6f6', sharex=ax1)


	ax1 = fig.add_axes(rect1, facecolor='#f6f6f6')  
	ax1.set_xlabel('date')

	ax1.set_title('Whalepool Messages, Gif & User joins per hour over price', fontsize=20, fontweight='bold')
	ax1.xaxis_date()

	fooCandlestick(ax1, candles.values, width=bar_width, colorup='g', colordown='k',alpha=0.9)
	# fooCandlestick(ax2, candles.values, width=0.864, colorup='g', colordown='k',alpha=0.9)
	ax1.set_ylabel('Bitcoin Price', color='g', size='large')
	fig.autofmt_xdate()


	# STICKERS
	gifs['count'] = gifs['count'].astype(float)
	gifvals = gifs['count'].values
	vmax = gifvals.max()
	upper, middle, lower = ta.BBANDS(gifvals, timeperiod=20, nbdevup=2.05, nbdevdn=2, matype=0)
	gifs['upper'] = upper
	mask = gifs['count'] > gifs['upper']

	ax2.set_ylabel('Gifs', color='g', size='large')
	ax2.bar(gifs['date'].values, gifvals,color='#7f7f7f',width=bar_width,align='center')
	ax2.plot( gifs['date'].values, upper, color='#FFA500', alpha=0.3 )
	ax2.bar(gifs[mask]['date'].values, gifs[mask]['count'].values,color='#e53ce8',width=bar_width,align='center')

	# MESSAGES
	msgs['count'] = msgs['count'].astype(float)
	messages = msgs['count'].values
	vmax = messages.max()
	upper, middle, lower = ta.BBANDS(messages, timeperiod=20, nbdevup=2.05, nbdevdn=2, matype=0)
	msgs['upper'] = upper
	mask = msgs['count'] > msgs['upper']

	ax3.set_ylabel('Messages', color='g', size='large')
	ax3.bar(msgs['date'].values, messages,color='#7f7f7f',width=bar_width,align='center')
	ax3.plot( msgs['date'].values, upper, color='#FFA500', alpha=0.3 )
	ax3.bar(msgs[mask]['date'].values, msgs[mask]['count'].values,color='#4286f4',width=bar_width,align='center')


	# User joins
	userjoins['count'] = userjoins['count'].astype(float)
	macd, macdsignal, macdhist = ta.MACD(userjoins['count'].values, fastperiod=12, slowperiod=26, signalperiod=9)
	np.nan_to_num(macdhist)

	growing_macd_hist = macdhist.copy()
	growing_macd_hist[ growing_macd_hist < 0 ] = 0



	ax4.set_ylabel('User Joins Momentum', color='g', size='large')
	ax4.plot(userjoins['date'].values, macd, color='#4449EC', lw=2)
	ax4.plot(userjoins['date'].values, macdsignal, color='#F69A4E', lw=2)
	ax4.bar(userjoins['date'].values, macdhist,color='#FB5256',width=bar_width,align='center')
	ax4.bar(userjoins['date'].values, growing_macd_hist,color='#4BF04F',width=bar_width,align='center')





	#im = Image.open(LOGO_PATH)	
	#fig.figimage(   im,   105,  (fig.bbox.ymax - im.size[1])-29)
	PATH_MSGS_OVER_PRICE = PATH+"messages_over_price.png"

	plt.savefig(PATH_MSGS_OVER_PRICE, bbox_inches='tight')


	msg = bot.sendPhoto(chat_id=WP_ROOM, photo=open(PATH_MSGS_OVER_PRICE,'rb'), caption="Whalepool Messages, Gif & User joins per hour over price" )
	bot.sendMessage(chat_id=chat_id, text="'Whalepool Messages, Gif & User joins per hour over price' posted to "+ROOM_ID_TO_NAME[WP_ROOM] )

	os.remove(PATH_MSGS_OVER_PRICE)


	# bot.sendMessage(chat_id=61697695, text="Posting... sometimes this can cause the telegram api to 'time out' ? so won't complete posting but trying anyway.." )

	# profile_pics = bot.getUserProfilePhotos(user_id=user_id)
	# for photo in profile_pics['photos'][0]:
	# 	if photo['height'] == 160:
	# 		bot.sendPhoto(chat_id=61697695, photo=photo['file_id'])
	# 		new_file = bot.getFile(photo['file_id'])
	# 		new_file.download('telegram.jpg')
	# 		pprint(photo.__dict__)



# Special function for testing purposes 
@restricted
def special(bot, update):
	user_id = update.message.from_user.id 
	chat_id = update.message.chat_id
	if user_id == 61697695:

		# Test Emoji
		text = ''
		# Red 
		text += '❤'
		# Orange
		text += '💛'
		# Green 
		text += '💚'
		# Blue 
		text += '💙'
		# Black
		text += '🖤'

		bot.sendMessage(chat_id=61697695, text=text )


#################################
#		BOT EVENT HANDLING		


def new_chat_member(bot, update):
	""" Welcomes new chat member """

	user_id = update.message.from_user.id 
	message_id = update.message.message_id 
	chat_id = update.message.chat.id
	name = get_name(update.message._new_chat_members)

	if (chat_id == WP_ROOM) or (chat_id == SP_ROOM) or (chat_id == WP_WOMENS):
		# Check user has a profile pic.. 

		timestamp = datetime.datetime.utcnow()

		info = { 'user_id': user_id, 'chat_id': chat_id, 'timestamp': timestamp }
		db.room_joins.insert(info)


		profile_pics = bot.getUserProfilePhotos(user_id=user_id)
		if profile_pics.total_count == 0:
			pprint("USER NEEDS A PROFILE PIC")


		restricted = 0

		# Bot was added to a group chat
		if update.message._new_chat_members.username == BOTNAME:
			return False
		# Another user joined the chat
		else:

			pprint('Room: '+str(ROOM_ID_TO_NAME[chat_id]))
			pprint('Chat_id: '+str(chat_id))
			pprint('Last Msgs: '+str(PRIOR_WELCOME_MESSAGE_ID))
			pprint('Last Msgs [ chat_id ]: '+str(PRIOR_WELCOME_MESSAGE_ID[chat_id]))

			try:
				if PRIOR_WELCOME_MESSAGE_ID[chat_id] > 0: 
					bot.delete_message(chat_id=chat_id, message_id=PRIOR_WELCOME_MESSAGE_ID[chat_id])
			except:
				pass


			#if len(name) > 50: 
			#	if chat_id in ROOM_ID_TO_NAME:
			#		bot.restrict_chat_member(chat_id, user_id, until_date=(datetime.datetime.now() + relativedelta(years=2)), can_send_messages=False, can_send_media_messages=False, can_send_other_messages=False, can_add_web_page_previews=False)



		
			logger.info("welcoming - "+name)
			msg = random.choice(MESSAGES['welcome']) % (name)

			if (chat_id == WP_WOMENS):
				msg = (MESSAGES['welcomewomen'] % (name))

			if profile_pics.total_count == 0:
				msg += " - Also, please set a profile pic!!"
			message = bot.sendMessage(chat_id=chat_id,reply_to_message_id=message_id,text=msg)     

			PRIOR_WELCOME_MESSAGE_ID[chat_id] = int(message.message_id)


	if (chat_id == MH_ROOM) :
		bot.restrict_chat_member(MH_ROOM, user_id, until_date=(datetime.datetime.now() + relativedelta(years=2)), can_send_messages=False, can_send_media_messages=False, can_send_other_messages=False, can_add_web_page_previews=False)

	if (chat_id == WP_WOMENS):
		bot.restrict_chat_member(WP_WOMENS, user_id, until_date=(datetime.datetime.now() + relativedelta(years=2)), can_send_messages=False, can_send_media_messages=False, can_send_other_messages=False, can_add_web_page_previews=False)

	if chat_id == WP_ROOM :
		bot.restrict_chat_member(WP_ROOM, user_id, until_date=(datetime.datetime.now() + relativedelta(days=14)), can_send_messages=False, can_send_media_messages=False, can_send_other_messages=False, can_add_web_page_previews=False)





def left_chat_member(bot, update):
	""" Says Goodbye to chat member """
	# Disabled # Spammy # Not needed # Zero Value add 
	return False 

	# name = get_name(update.message.from_user)
	# logger.info(message.left_chat_member.first_name+' left chat '+message.chat.title)
	# name = get_name(update.message.from_user)
	# msg = random.choice(MESSAGES['goodbye']) % (name)
	# bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 



# Just log/handle a normal message
def log_message_private(bot, update):
#	pprint(update.__dict__, indent=4)
	# pprint(update.message.__dict__, indent=4)
	username = update.message.from_user.username 
	user_id = update.message.from_user.id 
	message_id = update.message.message_id 
	chat_id = update.message.chat.id
	name = get_name(update.message.from_user)

	logger.info("Private Log Message: "+name+" said: "+update.message.text)

	# msg = bot.forwardMessage(chat_id=FORWARD_PRIVATE_MESSAGES_TO, from_chat_id=chat_id, message_id=message_id)

	msg = bot.sendMessage(chat_id=chat_id, text=(MESSAGES['start'] % name),parse_mode="Markdown",disable_web_page_preview=1)


# Just log/handle a normal message
def echo(bot, update):
	username = update.message.from_user.username 
	user_id = update.message.from_user.id 
	message_id = update.message.message_id 
	chat_id = update.message.chat.id

	if username != None:
		message = username+': '+update.message.text
		pprint(str(chat_id)+" - "+str(message))
	
		name = get_name(update.message.from_user)
		timestamp = datetime.datetime.utcnow()

		info = { 'user_id': user_id, 'chat_id': chat_id, 'message_id':message_id, 'message': message, 'timestamp': timestamp }
		db.natalia_textmessages.insert(info)

		info = { 'user_id': user_id, 'name': name, 'username': username, 'last_seen': timestamp }
		db.users.update_one( { 'user_id': user_id }, { "$set": info }, upsert=True)


	else:
		print("Person chatted without a username")


def photo_message(bot, update):
	user_id = update.message.from_user.id 
	message_id = update.message.message_id 
	chat_id = update.message.chat.id
	caption = update.message.caption

	# Picture has a caption ? 
	if caption != None:

		# Find hashtags in the caption
		hashtags = re.findall(r'#\w*', caption)

		# Did we find any ? 
		if len(hashtags) > 0:

			# Any matching ones, default = False
			legit_hashtag = False

			# Itterate hashtags 
			for e in hashtags:
				if legit_hashtag == False:
					legit_hashtag = forward_hashtags.get(e,False)

			# Post is allowed to be forwarded 
			if legit_hashtag != False:
				bot.forwardMessage(chat_id=legit_hashtag, from_chat_id=chat_id, message_id=message_id)


	if user_id == 61697695:
		pprint('Photo / Picture')
		pprint(update.message.__dict__)
		for p in update.message.photo:
			pprint(p.__dict__)



def sticker_message(bot, update):
	user_id = update.message.from_user.id
	message_id = update.message.message_id 
	chat_id = update.message.chat.id 
	timestamp = datetime.datetime.utcnow()
	username = update.message.from_user.username 
	name = get_name(update.message.from_user)

	# if chat_id in LOG_ROOMS: 
	if chat_id: 

		pprint('STICKER')
		
		sticker_id = update.message.sticker.file_id
		
		# file = bot.getFile(sticker_id)
		pprint(update.message.sticker.__dict__)
		# pprint(file.__dict__)
		
		if username != None:
			info = { 'user_id': user_id, 'chat_id': chat_id, 'message_id': message_id, 'sticker_id': sticker_id, 'timestamp': timestamp }
			db.natalia_stickers.insert(info)

			info = { 'user_id': user_id, 'name': name, 'username': username, 'last_seen': timestamp }
			db.users.update_one( { 'user_id': user_id }, { "$set": info }, upsert=True)




def video_message(bot, update):
	user_id = update.message.from_user.id 
	message_id = update.message.message_id 
	chat_id = update.message.chat.id
	timestamp = datetime.datetime.utcnow()
	name = get_name(update.message.from_user)

	pprint('VIDEO')

	# Not doing anything with this yet


def document_message(bot, update):
	user_id = update.message.from_user.id 
	message_id = update.message.message_id 
	chat_id = update.message.chat.id
	timestamp = datetime.datetime.utcnow()
	username = update.message.from_user.username 
	name = get_name(update.message.from_user)



	if chat_id in LOG_ROOMS: 

		images = ['image/jpeg','image/png']
		if update.message.document.mime_type in images:

			if LASTUNCOMPRESSED_IMAGES[chat_id] > 0: 
				bot.delete_message(chat_id=chat_id, message_id=LASTUNCOMPRESSED_IMAGES[chat_id])

			bot.delete_message(chat_id=chat_id, message_id=message_id)
			message = bot.sendMessage(chat_id=chat_id, text=name+", I deleted that pic you just posted because it is an uncompressed format, please use the \'compress\' format when posting pictures.",parse_mode="Markdown",disable_web_page_preview=1)
			LASTUNCOMPRESSED_IMAGES[chat_id] = int(message.message_id)

		

		if update.message.document.mime_type == 'video/mp4':

			pprint('VIDEO')
			
			file_id = update.message.document.file_id
		
			if username != None:
				info = { 'user_id': user_id, 'chat_id': chat_id, 'message_id': message_id, 'file_id': file_id, 'timestamp': timestamp }
				db.natalia_gifs.insert(info)

				info = { 'user_id': user_id, 'name': name, 'username': username, 'last_seen': timestamp }
				db.users.update_one( { 'user_id': user_id }, { "$set": info }, upsert=True)



def links_and_hashtag_messages(bot, update):
	user_id = update.message.from_user.id 
	message_id = update.message.message_id 
	chat_id = update.message.chat.id
	name = get_name(update.message.from_user)


	find_shill = re.findall(SHILL_DETECTOR, update.message.text)
	if (len(find_shill) > 0) and chat_id in ROOM_ID_TO_NAME:

		reply = 'Whalepool does not allow users to post personal affiliate links. This prevents many problems that can poison a community. Whalepool pays for all staff, servers, competitions and costs through affiliaite revenue, thus we ask users to support whalepool by using the community affiliate links instead.  ' 

		for s in COUNTER_SHILL: 

			found = re.findall(s['regex'], update.message.text) 
			if len(found) > 0: 
				reply += "\nThe user "+name+" recommended "+s['title']+", to signup on "+s['title']+" please use the following link: "+s['link']+""


		# Send message to mod chat that soemeone has shilled
		bot.sendMessage(chat_id=WP_ADMIN, text=name+" from "+ROOM_ID_TO_NAME[chat_id]+" posted a shill link",parse_mode="Markdown",disable_web_page_preview=1)

		# Forward the offending message to the mod room
		bot.forwardMessage(chat_id=WP_ADMIN, from_chat_id=chat_id, message_id=message_id)

		# Delete the offending message
		bot.delete_message(chat_id=chat_id, message_id=message_id)

		# Replace with the new replacement message
		bot.sendMessage(chat_id=chat_id, text=reply,parse_mode="Markdown",disable_web_page_preview=1)

		# Ban the bad actor
		bot.kick_chat_member(chat_id=chat_id, user_id=user_id)
			




	urls = [] 
	legit_hashtag = False
	for e in update.message.entities:
		ent = update.message.text[e.offset:(e.length+e.offset)]
		if e.type == 'hashtag':
			if ent != '' and ent != None:
				legit_hashtag = forward_hashtags.get(ent,False)

		if e.type == 'url':
			urls.append(ent)

	# Post is allowed to be forwarded 
	forward = False 
	if legit_hashtag != False:
		forward = legit_hashtag

	furlcnt = re.findall(FORWARD_URLS, update.message.text)
	if len(furlcnt) > 0 and ((chat_id == WP_ROOM) or (chat_id == MH_ROOM)):
		forward = WP_FEED
	if len(furlcnt) > 0 and (chat_id == SP_ROOM):
		forward = SP_FEED

	if forward != False:
		bot.forwardMessage(chat_id=forward, from_chat_id=chat_id, message_id=message_id)






#################################
# Command Handlers
logger.info("Setting  command handlers")
updater = Updater(bot=bot,workers=10)
dp      = updater.dispatcher

# Commands
dp.add_handler(CommandHandler('id', getid))
dp.add_handler(CommandHandler('start', start))
dp.add_handler(CommandHandler('about', about))
dp.add_handler(CommandHandler('rules', rules))
dp.add_handler(CommandHandler('admins', admins))
dp.add_handler(CommandHandler('teamspeak', teamspeak))
dp.add_handler(CommandHandler('telegram', telegram))
dp.add_handler(CommandHandler('livestream', livestream))
# dp.add_handler(CommandHandler('fomobot', fomobot))
dp.add_handler(CommandHandler('teamspeakbadges', teamspeakbadges))
dp.add_handler(CommandHandler('exchanges', exchanges))
dp.add_handler(CommandHandler('donation', donation))
dp.add_handler(CommandHandler('special', special))

dp.add_handler(CommandHandler('topstickers', topstickers))
dp.add_handler(CommandHandler('topgif', topgif))
dp.add_handler(CommandHandler('topgifposters', topgifposters))
dp.add_handler(CommandHandler('todayinwords', todayinwords))
dp.add_handler(CommandHandler('todaysusers', todaysusers))
dp.add_handler(CommandHandler('promotets', promotets))
dp.add_handler(CommandHandler('shill', shill))
dp.add_handler(CommandHandler('commandstats',commandstats))
dp.add_handler(CommandHandler('joinstats',joinstats))
dp.add_handler(CommandHandler('whalepooloverprice',whalepooloverprice))


# Welcome
dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_chat_member))

# Goodbye 
dp.add_handler(MessageHandler(Filters.status_update.left_chat_member, left_chat_member))

# Photo message
dp.add_handler(MessageHandler(Filters.photo, photo_message))

# Sticker message
dp.add_handler(MessageHandler(Filters.sticker, sticker_message))

# Video
dp.add_handler(MessageHandler(Filters.video, video_message))

# Links & Hashtags
dp.add_handler(MessageHandler((Filters.entity(MessageEntity.HASHTAG) | Filters.entity(MessageEntity.URL)), links_and_hashtag_messages))

# Documents 
dp.add_handler(MessageHandler(Filters.document, document_message))

# Someone private messages Natalia
dp.add_handler(MessageHandler(Filters.private, log_message_private))

# Normal Text chat
dp.add_handler(MessageHandler(Filters.text, echo))


# log all errors
dp.add_error_handler(error)



#################################
# Polling 
logger.info("Starting polling")
updater.start_polling()


# PikaWrapper()
	
	
	


	 