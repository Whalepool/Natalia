
# Datetime
import json  
from os.path import basename 

from pprint import pprint 
from utils.str import Str, log

class Errors:


	def __init__(self):
		pass 
		

	@staticmethod
	def check_for_errors(errors, errors_list):
		if errors > 0:
			for i in errors_list:
				log.error(str(i))
			exit()


