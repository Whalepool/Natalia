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
from PIL import ImageFont
from PIL import ImageDraw

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

from collections import defaultdict





def text_wrap(text, font, max_width):
    lines = []
    # If the width of the text is smaller than image width
    # we don't need to split it, just add it to the lines array
    # and return

    if font.getsize(text)[0] <= max_width:
        lines.append(text) 
    else:
        # split the line by spaces to get words
        words = text.split(' ')  
        i = 0
        # append every word to a line while its width is shorter than image width
        while i < len(words):
            line = ''         
            while i < len(words) and font.getsize(line + words[i])[0] <= max_width:                
                line = line + words[i] + " "
                i += 1
            if not line:
                line = words[i]
                i += 1
            # when the line gets longer than the max width do not append the word, 
            # add the line to the lines array
            lines.append(line)    
    return lines



"""
# Mongodb 
"""
client  = MongoClient('mongodb://localhost:27017')
db      = client.natalia_tg_bot



username = 'IamNomad'
profile_pic_filename = 'profile_pic_quote.jpg'


res = list(db.users.find({ 'username': username }))
if len(res) > 0 and username != '':
	do_user          = True 
	do_user_user_id  = res[0]['user_id'] 
	do_user_username = res[0]['username']


	# profile_pic = bot.get_user_profile_photos(do_user_user_id)
	# profile_pic = bot.getFile(profile_pic.photos[0][0].file_id)
	# profile_pic.download('profile_pic_quote.jpg')


	pprint(do_user)
	pprint(do_user_user_id)
	pprint(do_user_username)
	pprint(profile_pic_filename)




	res = list(db.natalia_textmessages.aggregate([
		{ "$match": { "user_id": do_user_user_id } },
	    {
	        "$redact": {
	            "$cond": [
	                { "$gt": [ { "$strLenCP": "$message" }, 100] },
	                "$$KEEP",
	                "$$PRUNE"
	            ]
	        }
	    },
	    { "$sample" : { "size": 1 } },
	    { "$limit": 1 },
	]))

	if len(res) > 0:

		msg = res[0]['message']
		msg = msg.split(':',1)[1].strip()

		# msg = "he says go up ? we go up.\nhe says we don't go up. we don't go up. \njust the way it is, very rarely doest price get out of his control and when it does u see the 5k bid walls as he has to make adjustments to continue playing the game "

		# open the background file
		img = Image.open('media/quote_bg_'+str(random.randint(0,1))+'.png')

		# size() returns a tuple of (width, height) 
		image_size = img.size 

		# create the ImageFont instance
		font_file_path = 'fonts/Roboto-Medium.ttf'
		font = ImageFont.truetype(font_file_path, size=50, encoding="unic")

		# get shorter lines
		lines = text_wrap(msg, font, image_size[0]-80)
		pprint(lines) 

		line_height = font.getsize('hg')[1]

		x = 40
		y = 40
		draw = ImageDraw.Draw(img)
		for line in lines:
			# draw the line on the image
			draw.text((x, y), line, fill='rgb(255, 255, 255)', font=font)

			# update the y position so that we can use it for next line
			y = y + line_height

		# save the image
		img.save('word2.png', optimize=True)



	else:

		# This user has no good quotes
		pass 


else:

	# Invalid username/no records found for username
	pass




