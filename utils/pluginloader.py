
# Datetime
import os, imp, mmap
from pprint import pprint 

class PluginLoader:

	def __init__(self):

		errors = 0 
		errors_list = []

		if 'plugin_folder' not in self.config:
			errors += 1
			errors_list.append('Missing plugin_folder from config')


		if 'plugin_main_module' not in self.config:
			errors += 1
			errors_list.append('Missing plugin_main_module from config')

		self.check_for_errors(errors, errors_list)

		self.plugin_folder = self.config['plugin_folder']
		self.main_module   = self.config['plugin_main_module']


	def getPlugins(self):

		plugins          = []
		# possible_plugins = os.listdir(self.plugin_folder)
		#  for i in possible_plugins:

		total_plugins = len(self.config['plugins'])

		for index, value in enumerate(self.config['plugins']):

			priority_index = (total_plugins-1) - index


			plugin_name = self.config['plugins'][index]['name']

			location = os.path.join(self.plugin_folder, plugin_name)
			
			# Check to make sure location is a folder 
			if not os.path.isdir(location):
				continue

			# Check for an __init__.py file 
			if not self.main_module + ".py" in os.listdir(location):
				continue

			# Check plugin has the following strings (requirements for plugins)
			required_strings = [
					{ 
						'string': 'run(Natalia, plugin_index, priority_index):',
						'error' : 'missing \"{string}\", This is the initial function executed to load and execute the plugin'
					},
					{
						'string': 'check_config_integrity',
						'error' : 'missing \"{string}\", It is required for plugins to have a config checking function in place to help users'
					},
					{
						'string': ' __init__(self, Natalia, plugin_index, priority_index)',
						'error' : 'missing \"{string}\", The plugins init function appears to be missing. '
					},
					{
						'string': 'add_handler',
						'error' : 'missing \"{string}\", The plugin doesnt add any handlers to any events or messages?'
					}
				]


			file_path = self.PATH+'/'+location+'/'+self.main_module+'.py'
			errors      = 0 
			errors_list = [] 
			with open(file_path, 'r') as file:
				data=file.read().replace('\n', '')
				for i in required_strings:
					if data.find(i['string']) == -1:
						errors += 1 
						errors_list.append('Plugin '+plugin_name+' - '+i['error'].format(string=i['string']))

			self.check_for_errors(errors, errors_list)




			info = imp.find_module(self.main_module, [location])
			plugins.append({"name": plugin_name, "plugin_index": index, "priority_index": priority_index, "info": info, "location": location})

		return plugins


	def loadPlugin(self, plugin):
		return imp.load_module(self.main_module, *plugin["info"])

