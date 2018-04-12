
"""
Available options from events file to predict upon.
['pid', 'action', 'operation', 'offset', 'size', 'timestamp', 'pre_wait_time', 'sync']

Right now the state has to be mantained here in the class, and only current
event will be provided as an argument
"""
class auto_stream(dict):
	def __init__(self):
		self["name"] = "auto_stream"
		pass

	def predict(self, event_row):
		return 0

	def __str__(self):
		return self["name"]
