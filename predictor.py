
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

"""
simple round robin predictor that will assign each request
a channel number in RR fashion. The stride decides when to
switch to the next queue. Since all writes are normalized
to 4096, the stride simply counts how many time a number has
been assigned then switch. e.g. if stride = 2, channel_id series
will be 0,0,1,1,2,2,...

Further assume 0 being the hottest queue and num_of_channel-1 as
the coldest queue. Always assign the data to be the coldest queue
"""
class rr_predictor:
	def __init__(self, num_of_channel, stride):
		self.num_of_channel = int(num_of_channel)
		self.curr_channel = 0
		self.stride = int(stride)
		self.stride_cnt = 0

	def predict(self, event_row):
		predicted_channel = self.curr_channel
		if self.stride == self.stride_cnt:
			self.curr_channel = (self.curr_channel + 1) % self.num_of_channel
			self.stride_cnt = 0
		else:
			self.stride_cnt += 1
		return predicted_channel

"""
simple markov predictor

Assign each LBA a initial state (e.g. coldest queue), when
the actual life time deviates from the predicted one, adjust
the counter towards the right direction until it can stablize

Further assume 0 being the hottest queue and num_of_channel-1 as
the coldest queue. Always assign the data to be the coldest queue
"""
class markov_pred_object:
	def __init__(self, initial_channel, last_access_time, hysteresis):
		# a mapping between LBA and last access time
		self.last_access_time = last_access_time
		# a mapping between LBA and predicted value
		self.predict_channel = initial_channel
		self.hysteresis_cnt = 0
		# hysteresis value to delay the update
		self.hysteresis_threshold = hysteresis
	def update_predictor(self, correct_channel, last_access_time):
		self.last_access_time = last_access_time
		# move the prediction towards larger if hysteresis
		# value is 0
		if correct_channel > self.predict_channel:
			if self.hysteresis_cnt == 0:
				self.predict_channel += 1
			else:
				self.hysteresis_cnt -= 1
		# move the prediction towards smaller one if hysteresis
		# value is 0
		elif correct_channel < self.predict_channel:
			if self.hysteresis_cnt == 0:
				self.predict_channel -= 1
			else:
				self.hysteresis_cnt -= 1
		# move the prediction towards more resistance to changes
		# if the prediction is correct
		else:
			if self.hysteresis_cnt < self.hysteresis_threshold:
				self.hysteresis_cnt += 1
	def get_prediction(self):
		return self.predict_channel

# channel boundary is the boundary to determine which channel is the ideal one
# format [a,b,c,d,e,...]
# |--ch0--|--ch1--|--ch2--|...
#         a       b       c...

class markov_predictor:
	def __init__(self, num_of_channel, hysteresis, channel_boundary):
		# a mapping between LBA and prediction
		self.pred_history = {}
		self.num_of_channel = num_of_channel
		self.hysteresis_threshold = hysteresis
		self.channel_boundary = channel_boundary
		assert len(channel_boundary) == num_of_channel - 1

	def predict(self, event_row):
		tokens = event_row.split(" ")
		addr = int(tokens[3])
		access_time = float(tokens[5])
		pred_entry = self.pred_history.get(addr)
		if pred_entry == None:
			self.pred_history.update({addr:markov_pred_object(self.num_of_channel - 1, access_time, self.hysteresis_threshold)})
			return self.num_of_channel - 1
		else:
			life_time = access_time - pred_entry.last_access_time
			# search optimal boundary
			correct_channel = 0
			for i in self.channel_boundary:
				if life_time < i:
					break
				else:
					correct_channel += 1
			pred_entry.update_predictor(correct_channel, access_time)
			return pred_entry.get_prediction()

# pred = markov_predictor(5, 1, [1,2,3,4])
# print(pred.predict("0 0 0 1024 2048 1.000 0 0"))
# print(pred.predict("0 0 0 1024 2048 2.000 0 0"))
# print(pred.predict("0 0 0 1024 2048 3.000 0 0"))
# print(pred.predict("0 0 0 1024 2048 3.000 0 0"))
# print(pred.predict("0 0 0 1024 2048 4.000 0 0"))
# print(pred.predict("0 0 0 1024 2048 5.000 0 0"))
# print(pred.predict("0 0 0 1024 2048 6.000 0 0"))
# print(pred.predict("0 0 0 1024 2048 7.000 0 0"))
# print(pred.predict("0 0 0 1024 2048 10.000 0 0"))
# print(pred.predict("0 0 0 1024 2048 13.000 0 0"))
# pred = rr_predictor(5, 2)
# print(pred.predict("0 0 0 1024 2048 2.000 0 0"))
# print(pred.predict("0 0 0 1024 2048 2.000 0 0"))
# print(pred.predict("0 0 0 1024 2048 2.000 0 0"))
# print(pred.predict("0 0 0 1024 2048 2.000 0 0"))
# print(pred.predict("0 0 0 1024 2048 2.000 0 0"))
# print(pred.predict("0 0 0 1024 2048 2.000 0 0"))
# print(pred.predict("0 0 0 1024 2048 2.000 0 0"))