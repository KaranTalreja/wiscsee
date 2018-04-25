import optparse

sector_size = 512
blk_size = 2048

class RawEvent:
    def __init__(self, pid, action, operation, offset, size,
            timestamp = None, pre_wait_time = None, sync = True):
        self.pid = int(pid)
        self.operation = operation
        self.offset = int(offset)
        self.size = int(size)
        self.sync = sync
        self.timestamp = timestamp
        self.pre_wait_time = pre_wait_time
        self.action = action
        self.life_time = 1000000.0
        assert action in ('D', 'C'), "action:{}".format(action)

        assert self.offset % sector_size == 0,\
            "offset {} is not aligned with sector size {}.".format(
            self.offset, sector_size)
        self.sector = self.offset / sector_size

        assert self.size % sector_size == 0, \
            "size {} is not multiple of sector size {}".format(
            self.size, sector_size)

        self.sector_count = self.size / sector_size

    def get_operation(self):
        return self.operation

    def get_type(self):
        return 'Event'

    def set_life_time(self, life_time):
    	self.life_time = life_time

    def __str__(self):
    	remaining_size = self.size
    	starting_addr = self.offset
    	str = ""
    	while remaining_size > 0:
    		str += ("{pid} {action} {operation} {addr} {size} {time} {pre_wait} {sync}"
    		.format(pid = self.pid, action = self.action, operation = self.operation, addr = starting_addr,
    			size = blk_size, time = self.timestamp, pre_wait = self.pre_wait_time, sync = self.sync))
    		remaining_size -= blk_size
    		starting_addr += blk_size
        return str

# ['pid', 'action', 'operation', 'offset', 'size', 'timestamp', 'pre_wait_time', 'sync']


parser = optparse.OptionParser()

parser.add_option('-i', '--input',
            action="store", dest="input",
            help="input file to be parsed")
parser.add_option('-o', '--output',
			action="store", dest="output",
			help="output file to be parsed")

options, args = parser.parse_args()

# first, split compound writes into small writes
#

of = open(options.output, 'w')

with open(options.input) as f:
    for line in f:
        tokens = line.split(' ')
        if tokens[1] == 'D' and tokens[2] != "read":
        	# decompose compound write to small writes
        	event = RawEvent(tokens[0], tokens[1], tokens[2], tokens[3], tokens[4], tokens[5], tokens[6], tokens[7])
        	of.write(str(event))
of.close()
f.close()

pending_list = {}
settled_list = {}
lastaccess_list = {}

with open(options.output) as f:
	for line in f:
		tokens = line.split(' ')
		assert tokens[2] != "read"
		addr = int(tokens[3])
		born = float(tokens[5])
		# first, search the pending_list to see if anything need to be resolved
		settled_query = settled_list.get(addr)
		if settled_query == None:
			pending_query = pending_list.get(addr)
			if pending_query == None:
				pending_list.update({addr:born})
			else:
				life = born - pending_query
				pending_list.pop(addr)
				settled_list.update({addr:[life]})
		else:
			settled_query.append(born - lastaccess_list.get(addr))

		last_query = lastaccess_list.get(addr)
		if last_query == None:
			lastaccess_list.update({addr:born})
		else:
			lastaccess_list[addr]=born

print(pending_list)
print(settled_list)