
# Datetime
import json  
from os.path import basename 
from datetime import datetime 

from pprint import pprint 

def now():
	return str(datetime.now())

class Str:


	def __init__(self):
		pass 


	@staticmethod
	def mogrify(topic, msg):
		""" json encode the message and prepend the topic """
		return topic + ' ' + json.dumps(msg)

	@staticmethod
	def demogrify(topicmsg):
		""" Inverse of mogrify() """
		json0 = topicmsg.find('[')
		json1 = topicmsg.find('{')

		start = json0
		if (json1 > 0):
			if (json0 > 0):
				if (json1 < json0):
					start = json1
			else:
				start = json1

		topic = topicmsg[0:start].strip()
		msg = json.loads(topicmsg[start:])

		return topic, msg 



class log:

	header    = '\033[95m'
	header2   = '\033[96m'
	ok_blue   = '\033[94m'
	ok_green  = '\033[92m'
	warning   = '\033[91m'
	fail      = '\033[90m'
	endc      = '\033[0m'
	bold      = '\033[1m'
	underline = '\033[4m'
	spacer    = '--------------------'

	@staticmethod
	def title(txt):
		print(now(), log.ok_green, log.bold, log.spacer, txt, log.spacer, log.endc)

	@staticmethod
	def subtitle(txt):
		print(now(), log.bold, txt, log.endc)

	@staticmethod
	def heading(txt):
		print(now(), log.header, txt, log.endc)

	@staticmethod
	def heading2(txt):
		print(now(), log.header2, txt, log.endc )

	@staticmethod
	def print(txt):
		print(now(), log.ok_blue, txt, log.endc)

	@staticmethod
	def error(txt):
		print(now(), log.warning, txt, log.endc)




