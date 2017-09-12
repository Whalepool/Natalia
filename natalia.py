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
import re 
import os
import sys
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

from PIL import Image


##################################
# Configure Logging

FORMAT = '%(asctime)s -- %(levelname)s -- %(module)s %(lineno)d -- %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger('root')
logger.info("Running "+sys.argv[0])


def check_envs(envars):
    # Check ENV variables
    errors = 0 
    for v in envars:
        if os.environ.get(v) is not None:
            logger.info('Found env var: '+v)
            pass
        else:
            errors += 1 
            logger.info('Please set a '+v+' envionment variable.')

    if errors > 0:
        sys.exit()



#################################
#			CONFIG 		
check_envs(['NATALIA_BOT_DIR', 'NATALIA_BOT_USERNAME', 'NATALIA_BOT_TOKEN'])


# Mongodb 
client      = MongoClient('mongodb://localhost:27017')
db          = client.whalepool

# Local dir of Natalia execution eg: /home/username/natalia 
PATH        = os.environ.get('NATALIA_BOT_DIR')

# Botname / Token
BOTNAME     = os.environ.get('NATALIA_BOT_USERNAME')
TELEGRAM_BOT_TOKEN = os.environ.get('NATALIA_BOT_TOKEN')



# Rooms 
WP_ROOM     = -1001012147388      # Whalepool
SP_ROOM     = -1001120581521      # Shitpool
WP_ADMIN    = -238862165          # Whalepool Admin
TEST_ROOM   = -1001137380400      # Test room
WP_FEED     = "@whalepoolbtcfeed" # Whalepool Feed

ROOM_ID_TO_NAME = {
	WP_ROOM : 'Whalepool',
	SP_ROOM : 'Shitpool',
	WP_ADMIN: 'Whalepool Mod room'
}

# Rooms where chat/gifs/etc is logged for stats etc 
LOG_ROOMS = [ WP_ROOM, SP_ROOM, TEST_ROOM ]

# Admin of Natalia 
ADMINS = [ 
	61697695,  # flibbr
	124588907, # spofas
	172018489, # saj
	136921994, # boxer
	174486191  # pysiek
]

# Chat id of where to send private messages to natalia to "help i am banned.." etc 
FORWARD_PRIVATE_MESSAGES_TO = 61697695 #flibbr

# Storing last 'welcome' message ids 
PRIOR_WELCOME_MESSAGE_ID = {
	WP_ROOM   : 0,
	SP_ROOM   : 0,
	TEST_ROOM : 0
}

# Storing last 'removal' of uncompress images, message ids
LASTUNCOMPRESSED_IMAGES = { 
	WP_ROOM   : 0,
	SP_ROOM   : 0,
	TEST_ROOM : 0
}

# Hashtags that forward messages to specific channels
forward_hashtags = {
	'#communityfund' : WP_FEED,
	'#community' : WP_FEED
}

# Allowed URLS to auto-forward to feed room
forward_urls = r"reddit.com(?!\/r\/ethtrader)|medium.com|marketwatch.com|investopedia.com|forklog.com|businessinsider|cnbc.com|newsbtc.com|ledgerx.com|cftc.gov|bitcointicker.co|coin.dance|bloomberg.com|tradingview.com|cointelegraph.com|coindesk.com|github.com|youtube.com|bitsonline.com"

# List of admins that users can request 
ADMINS_JSON = { 
	"@flibbr" 	  : { 
		"adminOf" : "Teamspeak (Trading Dojo) / Whalepool Telegram",
		"about"   : "Low tolerance for Low IQ users degrading the telegram chat & mindless chatter on teamspeak"
	},
	"@Mayvune"    : { 
		"adminOf" : "Whalepool Telegram & TeamSpeak Mod",
		"about"   : "We are all mad here. DOOM is coming!"
	},
	"@gonzoucab"  : { 
		"adminOf" : "Whalepool Telegram",
		"about"   : "No trial, no nothing."
	},
	"@notdao"     : {
		"adminOf" : "Shitpool Telegram",
		"about"   : "Likes: information. Dislikes: misinformation"
	},
	"@wawin"     : {
		"adminOf" : "Whalepool Telegram",
		"about"   : "I'm a simple man; I see shill post, I ban."
	},
	"@grammi"     : {
		"adminOf" : "Whalepool Telegram",
		"about"   : "no gamble... no future"
	},
	"@Saj\_le\_Great"     : {
		"adminOf" : "Whalepool Telegram",
		"about"   : "All your dips belong to me i BTFD before it was kewl ."
	},
	"@cshrem"     : {
		"adminOf" : "Whalepool Telegram",
		"about"   : "Please short Bitcoin, we need moar rocket fuel."
	}
}

# Welcome/Goodbye message templates 
MESSAGES = {
      "welcome": [
      	  "Hi there %s you big bad crypto boy. I'm the Whalepool secretary(bot). Send me a PM (@WPrules_bot) to learn how to push my buttons & get to know the rules.",
      	  "Hi %s I'm Natalia, resident chat secretary. I do exactly as I am told like a good girl. PM me (@WPrules_bot) if you want to know the rules i play by.",
      	  "%s! Hi! Welcome, I live to serve. PM me (@WPrules_bot) so we can get more aquainted with my rules.",
      	  "Hi there %s, I'm Natalia, group secretary. You dont have to tie me up to control me, just send me a PM (@WPrules_bot) to get house rules."
      ],
      "goodbye": [
      	"Smells better without ya %s",
      	"The average net worth of this group just shot up when %s left",
      	"goodbye %s. It was fun whilte it lasted",
      	"see ya %s, my sweet love"
      ],
      "pmme": [
      	"Naughty naughty %s, you know we can't talk dirty in public. PM me for that kind of talk & house rules.",
      	"Sorry %s, I'd love to service you in public, but Telegram only lets me do you in private. PM me for house rules.",
      	"Sorry %s I'm a shy bot so you have to PM to use my functions & house rules.",
      	"%s, I'm a shy girl, I like to do these things in private. Can you PM me for house rules & our safe word?", 
      	"%s, some things a better left for behind closed doors. PM me for house rules." 
      ],
      "countershill": {
      	  "default": "BEWARE: UNAUTHORISED LINKS MAY CONTAIN VIRUSES, ONLY USE OFFICIAL WHALEPOOL URLS\n\nWe recommend users point people to https://whalepool.io/exchanges - Here we recommend a variety of exchanges and platforms. The affiliate links are shared whalepool.io links so any revnue generated to go back into the community your using right now to help make it better. Thanks.",
      	  "simplefx": "BEWARE: UNAUTHORISED LINKS MAY CONTAIN VIRUSES, ONLY USE OFFICIAL WHALEPOOL URLS\n\nWe recommend users point people to http://simplefx.whalepool.io - This a community Whalepool.io based affiliate link. Using this link allows Whalepool.io to use revnue generated to go back into the community your using right now to help make it better. If you want to check out other alternative exchanges/brokers, you can also look at at https://whalepool.io/exchanges Thanks.",
      	  "onebroker": "BEWARE: UNAUTHORISED LINKS MAY CONTAIN VIRUSES, ONLY USE OFFICIAL WHALEPOOL URLS\n\nWe recommend users point people to http://1broker.whalepool.io - This a community whalepool.io based affiliate link. Using this link allows whalepool.io to use revnue generated to go back into the community your using right now to help make it better. If you want to check out other alternative exchanges/brokers, you can also look at at https://whalepool.io/exchanges Thanks.",
      	  "bitmex": "BEWARE: UNAUTHORISED LINKS MAY CONTAIN VIRUSES, ONLY USE OFFICIAL WHALEPOOL URLS\n\nWe recommend users point people to http://bitmex.whalepool.io - This a community whalepool.io based affiliate link. Using this link allows whalepool.io to use revnue generated to go back into the community your using right now to help make it better. If you want to check out other alternative exchanges/brokers, you can also look at at https://whalepool.io/exchanges Thanks."
      },
      "start": "Hi %s, Welcome to Whalepool\nPlease click one of the links to see how i can help you:\n\n/rules  - See Whalepool Rules\n/about - about us\n/admins - See list of admins to contact for help.\n/teamspeak - How to connect to teamspeak\n/telegram - Our telegram Channels\n/livestream - Listen to use live on youtube\n/fomobot - Learn about our Bitcoin/Crypto telegram bot\n/exchanges - See where we recommend to trade\n/donation - Make a donation",
      "about": "*About Whalepool*\n\nWe are a community trades & crypto lovers.\nFollow us on twitter: [@whalepool](https://twitter.com/whalepool)\nTalk to us on /teamspeak\nJoin our /telegram channels\nListen to our youtube livestream [http://livestream.whalepool.io](http://livestream.whalepool.io)\n\n/start - to go back to home",
      "wprules": "*Whalepool House Rules*\n\n*Bannable offenses*\n1) Don't post shill links or spam\n2) Don't scam or push scamcoins (unless in @shitpool) \n3) Don't post excessive unrelated gifs. Yes. Gifs are cool. No we don't want to see your whole collection.\n\n*Group Guidelines*\n1) Be on topic\n2) Contribute real content, don't overly forward or just shill your Twitter/YouTube account\n3) Don't blame other peoples ideas for your trading losses\n4) Make arguments of substance, not personal insults/ad hominems\n\n/start - to go back to home",
      "teamspeak": "[Whalepool Teamspeak](https://whalepool.io/connect/teamspeak) is our hosted voice chat.\nWe have 2 active rooms.\n\n*Freedom room*\nFor loose general crypto & non crypto related discussion\n\n*Trading Dojo*\nFor a quieter more price action focused voice chat\n\nDownload Teamspeak here: [https://www.teamspeak.com/downloads](https://www.teamspeak.com/downloads)\nConnect to: ts.whalepool.io or 158.69.115.146:50128\nMore connection instructions available here: [https://whalepool.io/connect/teamspeak](https://whalepool.io/connect/teamspeak)\n\n/start - to go back to home",
      "telegram": "*Whalepool main Chat telegram channels*:\n[Whalepool Chat](https://t.me/whalepoolbtc)\n^BTC/ETH (little LTC/XMR/ETC etc) - Mostly chat about the major cryptos\n[Shitpool Chat](https://t.me/shitpool)\n^Discussion about lesser known alts, icos, tokens, crowdsales.. etc\n\n*Non Chat - Feed/Broadcast channels*:\n[Whalepool Feed](https://t.me/whalepoolbtcfeed)\n^Feed from the whalepool channel\n[Shitpool Feed](https://t.me/shitcoincharts)\n^Broadcast (non chat) feed about altcoins on the move\n\n/start - to go back to home",
      "livestream": "*Whalepool Live Stream*\nListen to us live on Youtube\n[http://livestream.whalepool.io](http://livestream.whalepool.io)\n\n/start - to go back to home",
      "fomobot" : "*Whalepool Official FOMO BOT*\n\nFomo Bot is the official Whalepool Crypto market information bot. You can use this bot to query a whole range of useful market data.\n\nKeep in mind developing & running bots takes time & effort - Feel free to make a /donation\n\nStart a conversation with @FOMO\_bot & begin to unlock your potential.\n\nYou can also follow [@botfomo](https://twitter.com/botfomo) on twitter\n\n/start - to go back to home",
      "exchanges" : "*Whalepool Recommended Exchanges*\nFrom our experience, we only recommend trading on the following exchanges:\n\n*Spot Trading BTC/Alts*\n[Bitfinex](http://bitfinex.whalepool.io) - Proven track record. Great staff. The most liquid BTCUSD market. Find Bitfinex reps on /teamspeak also.\n\n*Bitcoin Futures*\n[Bitmex](http://bitmex.whalepool.io) - Proven track record, available in the whalepool /telegram chat also. A great platform with high leverage available\n\n*Forex/Commodity/Stocks*\n[1broker](http://1broker.whalepool.io) - Without a doubt, the cheapest & best CFD platform to use with your bitcoin. Including copy trade features. Proven track record. 1broker reps also available on /teamspeak\n\n/start - to go back to home",

      # "wprules": "*Whalepool House Rules*\n\n*Bannable offenses*\n1) Don't post shill links or spam\n2) Don't scam or push scamcoins (unless in @shitpool) \n3) Don't post excessive unrelated gifs. Yes. Gifs are cool. No we don't want to see your whole collection.\n\n*Group Guidelines*\n1) Be on topic\n2) Contribute real content, don't overly forward or just shill your Twitter/YouTube account\n3) Don't blame other peoples ideas for your trading losses\n5) Make arguments of substance, not personal insults/ad hominems",
      "signature": "\n\nJoin us on our [Teamspeak](https://whalepool.io/connect/teamspeak) and chat to us vocally.\n\nOur Telegram Rooms:\n[Whalepool Telegram Chat](http://telegram.whalepool.io)\n[Whalepool Telegram Botfeed](https://telegram.me/whalepoolbtcfeed)\n\nWebsite: [whalepool.io](http://whalepool.io)\nTwitter: [@whalepool](http://twitter.com/whalepool\nSubscribe to us on [WhalePool Youtube](https://www.youtube.com/channel/UCSAXsgdvfiS9WqAxwjMm8aQ):)",
      "donate": "If you would like to support Whalepool.io, please donate to:\n\nBitcoin: 175oRbKiLtdY7RVC8hSX7KD69WQs8PcRJA\n\nPlease be sure to let us know you donated :)",

      "admin_start": "%s, this is your admin control: \n\n /topgif - post the top gif to whalepool + feed\n/topgifposters - post who are the top 5 gif posters to whalepool\n/todayinwords - Today in words...\n/todaysusers - Wordcloiud of whos active today"
}


# Stop words for wordcloud 
EXTRA_STOPWORDS  = ['will','lol','need','BTC','bitcoin','new','one','see','yeah','good','Im','make','now','http','https','go','twitter','other','also','say']



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
def get_name(update):
        try:
            name = update.message.from_user.first_name
        except (NameError, AttributeError):
            try:
                name = update.message.from_user.username
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

	chat_id = update.message.chat.id
	message_id = update.message.message_id
	user_id = update.message.from_user.id 
	name = get_name(update)
	logger.info("/start - "+name)

	pprint(update.message.chat.type)

	if (update.message.chat.type == 'group') or (update.message.chat.type == 'supergroup'):
		msg = random.choice(MESSAGES['pmme']) % (name)
		bot.sendMessage(chat_id=chat_id,text=msg,reply_to_message_id=message_id, parse_mode="Markdown",disable_web_page_preview=1) 
	else:
		msg = MESSAGES['wprules']
		msg = bot.sendMessage(chat_id=chat_id, text=(MESSAGES['start'] % name),parse_mode="Markdown",disable_web_page_preview=1)

		if user_id in ADMINS:
			msg = bot.sendMessage(chat_id=chat_id, text=(MESSAGES['admin_start'] % name),parse_mode="Markdown",disable_web_page_preview=1)



def about(bot, update):

	chat_id = update.message.chat.id
	message_id = update.message.message_id
	name = get_name(update)
	logger.info("/about - "+name)

	if (update.message.chat.type == 'group') or (update.message.chat.type == 'supergroup'):
		msg = random.choice(MESSAGES['pmme']) % (name)
		bot.sendMessage(chat_id=chat_id,text=msg,reply_to_message_id=message_id, parse_mode="Markdown",disable_web_page_preview=1) 
	else:
		msg = MESSAGES['about']
		bot.sendMessage(chat_id=chat_id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 


def rules(bot, update):

	chat_id = update.message.chat.id
	message_id = update.message.message_id
	name = get_name(update)
	logger.info("/rules - "+name)

	if (update.message.chat.type == 'group') or (update.message.chat.type == 'supergroup'):
		msg = random.choice(MESSAGES['pmme']) % (name)
		bot.sendMessage(chat_id=chat_id,text=msg,reply_to_message_id=message_id, parse_mode="Markdown",disable_web_page_preview=1) 
	else:
		msg = MESSAGES['wprules']
		bot.sendMessage(chat_id=chat_id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 


def admins(bot, update):

	chat_id = update.message.chat.id
	message_id = update.message.message_id
	name = get_name(update)
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

		bot.sendMessage(chat_id=chat_id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 


def teamspeak(bot, update):

	chat_id = update.message.chat.id
	message_id = update.message.message_id
	name = get_name(update)
	logger.info("/teamspeak - "+name)

	if (update.message.chat.type == 'group') or (update.message.chat.type == 'supergroup'):
		msg = random.choice(MESSAGES['pmme']) % (name)
		bot.sendMessage(chat_id=chat_id,text=msg,reply_to_message_id=message_id, parse_mode="Markdown",disable_web_page_preview=1) 
	else:
		msg = MESSAGES['teamspeak']
		bot.sendSticker(chat_id=chat_id, sticker="CAADBAADqgIAAndCvAiTIPeFFHKWJQI", disable_notification=False)
		bot.sendMessage(chat_id=chat_id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 


		
def telegram(bot, update):

	chat_id = update.message.chat.id
	message_id = update.message.message_id
	name = get_name(update)
	logger.info("/telegram - "+name)

	if (update.message.chat.type == 'group') or (update.message.chat.type == 'supergroup'):
		msg = random.choice(MESSAGES['pmme']) % (name)
		bot.sendMessage(chat_id=chat_id,text=msg,reply_to_message_id=message_id, parse_mode="Markdown",disable_web_page_preview=1) 
	else:
		msg = MESSAGES['telegram']
		bot.sendMessage(chat_id=chat_id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 


def livestream(bot, update):

	chat_id = update.message.chat.id
	message_id = update.message.message_id
	name = get_name(update)
	logger.info("/livestream - "+name)

	if (update.message.chat.type == 'group') or (update.message.chat.type == 'supergroup'):
		msg = random.choice(MESSAGES['pmme']) % (name)
		bot.sendMessage(chat_id=chat_id,text=msg,reply_to_message_id=message_id, parse_mode="Markdown",disable_web_page_preview=1) 
	else:
		msg = MESSAGES['livestream']
		bot.sendSticker(chat_id=chat_id, sticker="CAADBAADcwIAAndCvAgUN488HGNlggI", disable_notification=False)
		bot.sendMessage(chat_id=chat_id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 


def fomobot(bot, update):

	chat_id = update.message.chat.id
	message_id = update.message.message_id
	name = get_name(update)
	logger.info("/fomobot - "+name)

	if (update.message.chat.type == 'group') or (update.message.chat.type == 'supergroup'):
		msg = random.choice(MESSAGES['pmme']) % (name)
		bot.sendMessage(chat_id=chat_id,text=msg,reply_to_message_id=message_id, parse_mode="Markdown",disable_web_page_preview=1) 
	else:
		msg = MESSAGES['fomobot']
		bot.sendMessage(chat_id=chat_id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 


def exchanges(bot, update):

	chat_id = update.message.chat.id
	message_id = update.message.message_id
	name = get_name(update)
	logger.info("/exchanges - "+name)

	if (update.message.chat.type == 'group') or (update.message.chat.type == 'supergroup'):
		msg = random.choice(MESSAGES['pmme']) % (name)
		bot.sendMessage(chat_id=chat_id,text=msg,reply_to_message_id=message_id, parse_mode="Markdown",disable_web_page_preview=1) 
	else:
		msg = MESSAGES['exchanges']
		bot.sendMessage(chat_id=chat_id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 
		bot.forwardMessage(chat_id=WP_ADMIN, from_chat_id=chat_id, message_id=message_id)


def donation(bot, update):

	chat_id = update.message.chat.id
	message_id = update.message.message_id
	name = get_name(update)
	logger.info("/donation - "+name)

	if (update.message.chat.type == 'group') or (update.message.chat.type == 'supergroup'):
		msg = random.choice(MESSAGES['pmme']) % (name)
		bot.sendMessage(chat_id=chat_id,text=msg,reply_to_message_id=message_id, parse_mode="Markdown",disable_web_page_preview=1) 
	else:
		bot.sendPhoto(chat_id=chat_id, photo="AgADBAADlasxG4uhCVPAkVD5G4AaXgtKXhkABL8N5jNhPaj1-n8CAAEC",caption="Donations by bitcoin to: 175oRbKiLtdY7RVC8hSX7KD69WQs8PcRJA")


####################################################
# ADMIN FUNCTIONS

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
		user = bot.getChat(u['_id'])
		msg += "\n#"+str(i+1)+" - "+user['first_name']+" with "+str(u['total'])+" gifs"


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



# Special function for testing purposes 
@restricted
def special(bot, update):
	user_id = update.message.from_user.id 
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


		# profile_pics = bot.getUserProfilePhotos(user_id=user_id)
		# for photo in profile_pics['photos'][0]:
		# 	if photo['height'] == 160:
		# 		bot.sendPhoto(chat_id=61697695, photo=photo['file_id'])
		# 		new_file = bot.getFile(photo['file_id'])
		# 		new_file.download('telegram.jpg')
		# 		pprint(photo.__dict__)





#################################
#		BOT EVENT HANDLING		


def new_chat_member(bot, update):
	""" Welcomes new chat member """

	user_id = update.message.from_user.id 
	message_id = update.message.message_id 
	chat_id = update.message.chat.id
	name = get_name(update)

	if (chat_id == WP_ROOM) or (chat_id == SP_ROOM):
		# Check user has a profile pic.. 
		profile_pics = bot.getUserProfilePhotos(user_id=user_id)
		if profile_pics.total_count == 0:
			pprint("USER NEEDS A PROFILE PIC")


		# Bot was added to a group chat
		if update.message._new_chat_member.username == BOTNAME:
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

		
			logger.info("welcoming - "+name)
			msg = random.choice(MESSAGES['welcome']) % (name)
			if profile_pics.total_count == 0:
				msg += " - Also, please set a profile pic!!"
			message = bot.sendMessage(chat_id=chat_id,reply_to_message_id=message_id,text=msg)     

			PRIOR_WELCOME_MESSAGE_ID[chat_id] = int(message.message_id)



def left_chat_member(bot, update):
	""" Says Goodbye to chat member """
	# Disabled # Spammy # Not needed # Zero Value add 
	return False 

	# name = get_name(update)
	# logger.info(message.left_chat_member.first_name+' left chat '+message.chat.title)
	# name = get_name(update)
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
	name = get_name(update)

	logger.info("Private Log Message: "+name+" said: "+update.message.text)

	msg = bot.forwardMessage(chat_id=FORWARD_PRIVATE_MESSAGES_TO, from_chat_id=chat_id, message_id=message_id)

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
	
		name = get_name(update)
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
	name = get_name(update)

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
	name = get_name(update)

	pprint('VIDEO')

	# Not doing anything with this yet


def document_message(bot, update):
	user_id = update.message.from_user.id 
	message_id = update.message.message_id 
	chat_id = update.message.chat.id
	timestamp = datetime.datetime.utcnow()
	username = update.message.from_user.username 
	name = get_name(update)



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

	furlcnt = re.findall(forward_urls, update.message.text)
	if len(furlcnt) > 0 and (chat_id == WP_ROOM):
		forward = WP_FEED

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
dp.add_handler(CommandHandler('fomobot', fomobot))
dp.add_handler(CommandHandler('exchanges', exchanges))
dp.add_handler(CommandHandler('donation', donation))
dp.add_handler(CommandHandler('special', special))

dp.add_handler(CommandHandler('topgif', topgif))
dp.add_handler(CommandHandler('topgifposters', topgifposters))
dp.add_handler(CommandHandler('todayinwords', todayinwords))
dp.add_handler(CommandHandler('todaysusers', todaysusers))

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
	
	
	


	 