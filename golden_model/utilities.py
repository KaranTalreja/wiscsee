#! /usr/bin/python3

# See LICENSE for license details.

import sys
import getopt
import math
import globals
import numpy
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

globals.init()
numpy.seterr(divide='ignore', invalid='ignore')

############################# Class Defines ####################################
# Struct for storing info for differnet sectors
class SectorInfo():

    def __init__(self):
        self.sector_addr = 0
        self.operation_times = []
        self.operation_type = []
        self.life_times = []
        self.queue_num = []
        self.std_dev = 0

# Struct for storing info for differnet sectors
class ChunkInfo():

    def __init__(self):
        self.chunk_addr = 0
        self.life_tuples = []
        self.queue_num = []

# Info for each physical sector
class PhysicalSectorInfo():

    def __init__(self):
        self.logical_sector_addr = 0
        self.physical_sector_addr = 0
        self.birth_time = 0
        self.death_time = 0
        self.life_time = 0

# Info for each physical sector
class QueueInfo():

    def __init__(self):
        self.sectors_list = []
        self.max_death_time = 0
        self.mean_death_time = 0
        self.size = 0

############################# Function Defines #################################

# Function for sorting physical sectors based on the creation time
def UpdateSectorsPerBlock():

    globals.sectors_per_block = globals.block_size/globals.sector_size

# Take the inputs
def GetArgs(argv):

    found_input_file = False

    try:
        opts, args = getopt.getopt(argv,"hi:s:b:t:q:c:",["ifile=", \
        "sector_size", "block_size", "total_size", "queue_entries", \
        "chunk_size"])
    except getopt.GetoptError:
        print ('ERROR: golden_model_gen.py')
        print ('    -i <globals.input_file>')
        print ('    -s <sector_size>')
        print ('    -b <block_size>')
        print ('    -t <total_size>')
        print ('    -q <queue_entries>')
        print ('    -c <chunk_size in MB>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('test.py -i <globals.input_file>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            globals.input_file = arg
            found_input_file = True
        elif opt in ("-s", "--globals.sector_size"):
            globals.sector_size = arg
            UpdateSectorsPerBlock()
        elif opt in ("-b", "--globals.block_size"):
            globals.block_size = arg
            UpdateSectorsPerBlock()
        elif opt in ("-t", "--globals.total_size"):
            globals.total_size = arg
        elif opt in ("-q", "--queue_entries"):
            globals.queue_entries = int(arg)
        elif opt in ("-c", "--chunk_size"):
            globals.chunk_size = int(arg)
    if not found_input_file:
        print ("ERROR: -i was not given")
        sys.exit(2)

# Dividing lines into
def TraceParser(filename):

    with open(filename) as f:
        for line in f:
            globals.sectors.append(SectorInfo())
            line = line.split(' : ')
            globals.sectors[-1].sector_addr = line[0]
            line = line[1].split(' ')
            for i in range(len(line)):
                operations = line[i].split(',')
                globals.sectors[-1].operation_times.append\
                        (float(operations[0].rstrip()))
                globals.sectors[-1].operation_type.append\
                        (operations[1].rstrip())

# Create list of logical sectors
# Also this will add lifetimes to the logical sectors
def CreatePhysicalSectors():

    physical_addr = 0

    for logical_sector in range(len(globals.sectors)):
        for physical_sector in \
                range(len(globals.sectors[logical_sector].operation_times)):
            if globals.sectors[logical_sector].operation_type[physical_sector]\
                    == 'write':
                globals.physical_sectors.append(PhysicalSectorInfo())
                globals.physical_sectors[-1].logical_sector_addr = \
                    globals.sectors[logical_sector].sector_addr
                globals.physical_sectors[-1].physical_sector_addr = \
                    physical_addr
                physical_addr = physical_addr + 1
                globals.physical_sectors[-1].birth_time = \
                    globals.sectors[logical_sector].operation_times\
                    [physical_sector]
                if physical_sector != \
                len(globals.sectors[logical_sector].operation_times) \
                        - 1:
                    globals.physical_sectors[-1].death_time = \
                        globals.sectors[logical_sector].operation_times[\
                        physical_sector + 1]
                else:
                    globals.physical_sectors[-1].death_time = math.inf
                globals.physical_sectors[-1].life_time = \
                        globals.physical_sectors[-1].death_time - \
                        globals.physical_sectors[-1].birth_time
                #if globals.physical_sectors[-1].death_time != math.inf:
                globals.sectors[logical_sector].life_times.append(\
                    globals.physical_sectors[-1].death_time - \
                    globals.physical_sectors[-1].birth_time)

# Find location for a particular chunk
def GetChunkObj(chunk_address):
    for chunk_no in range(len(globals.chunks)):
        if chunk_address == globals.chunks[chunk_no].chunk_addr:
            return chunk_no
    globals.chunks.append(ChunkInfo())
    globals.chunks[-1].chunk_addr = chunk_address
    return (len(globals.chunks) - 1)

# Create chunks for the grouping
def CreateChunks():
    for physical_sector in range(len(globals.physical_sectors)):
        chunk_address = int(int(\
                globals.physical_sectors[physical_sector].logical_sector_addr)\
                / (globals.chunk_size * (2**20)))
        chunk_no = GetChunkObj(chunk_address)
        life_tuple = [globals.physical_sectors[physical_sector].birth_time, \
            globals.physical_sectors[physical_sector].death_time - \
            globals.physical_sectors[physical_sector].birth_time]
        globals.chunks[chunk_no].life_tuples.append(life_tuple)
        globals.chunks[chunk_no].life_tuples.sort(key=LifeTupleSortingFunc)

# Calculate standard deviation for all sectors
def CalculateStdDev():
    for logical_sector in range(len(globals.sectors)):
        globals.sectors[logical_sector].std_dev = \
                numpy.std(globals.sectors[logical_sector].life_times, \
                dtype=numpy.float64)

# Function for sorting physical sectors based on the creation time
def TimeSortingFunc(elem):
    return elem.birth_time

# Function for sorting life_tuples of chunks
def LifeTupleSortingFunc(elem):
    return elem[0]

# Create Graph values
def CreateGraph():
    dt_matric = []
    num_of_operations = []
    addr = []

    for logical_sector in range(len(globals.sectors)):
        dt_matric.append(globals.sectors[logical_sector].std_dev)
        num_of_operations.append\
                (len(globals.sectors[logical_sector].life_times))
        addr.append(globals.sectors[logical_sector].sector_addr)

    file_name = globals.input_file.split('.')
    plot_name = file_name[0] + '.png'

    fig, std_dev_plot = plt.subplots()
    color = 'tab:red'
    std_dev_plot.set_xlabel('Logical Block Adresses')
    std_dev_plot.set_ylabel('DT_matrix', color=color)
    std_dev_plot.plot(addr, dt_matric, 'ro', color=color)
    std_dev_plot.tick_params(axis='y', labelcolor=color)

    num_op_plot = std_dev_plot.twinx()

    color = 'tab:blue'
    num_op_plot.set_ylabel('# of operations', color=color)
    num_op_plot.plot(addr, num_of_operations, color=color)
    num_op_plot.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()
    plt.grid()
    plt.title(file_name[0])
    plt.savefig(plot_name)

def FindTimeRange():

    min_time = math.inf
    max_time = 0

    for logical_sector in range(len(globals.sectors)):

        if len(globals.sectors[logical_sector].life_times) > 0:

            for time in range(len(globals.sectors[logical_sector].life_times)):
                if (globals.sectors[logical_sector].life_times[time] \
                        > max_time) & \
                        (globals.sectors[logical_sector].life_times[time] != \
                        math.inf):
                    max_time = globals.sectors[logical_sector].life_times[time]
            if min(globals.sectors[logical_sector].life_times) < min_time:
                min_time = min(globals.sectors[logical_sector].life_times)

        globals.max_life_time = max_time
        globals.min_life_time = min_time

def AllocateGoldenQueues():

    life_time_range = globals.max_life_time - globals.min_life_time
    queue_step = life_time_range/(globals.queue_entries - 1)

    for logical_sector in range(len(globals.sectors)):

        if len(globals.sectors[logical_sector].life_times) > 0:
            for time in range(len(globals.sectors[logical_sector].life_times)):
                current_life_time = \
                    globals.sectors[logical_sector].life_times[time]
                allocated_queue = 0
                if current_life_time == math.inf:
                    allocated_queue = globals.queue_entries - 1
                else:
                    allocated_queue = math.floor(current_life_time/queue_step)
                globals.sectors[logical_sector].queue_num.append(allocated_queue)

def AllocateGoldenQueuesChunks():

    life_time_range = globals.max_life_time - globals.min_life_time
    queue_step = life_time_range/(globals.queue_entries - 1)

    for chunk_no in range(len(globals.chunks)):

        if len(globals.chunks[chunk_no].life_tuples) > 0:
            for tu in range(len(globals.chunks[chunk_no].life_tuples)):
                current_life_time = \
                    globals.chunks[chunk_no].life_tuples[tu][1]
                allocated_queue = 0
                if current_life_time == math.inf:
                    allocated_queue = globals.queue_entries - 1
                else:
                    allocated_queue = math.floor(current_life_time/queue_step)
                globals.chunks[chunk_no].queue_num.append(allocated_queue)

def CreateQueues():

    for x in range(int(globals.queue_entries)):
        globals.queue_list.append(QueueInfo())

def FindEmptyQueue():

    empty_queue_list = []

    for x in range(int(globals.queue_entries)):
        if globals.queue_list[x].size == 0:
            empty_queue_list.append(x)

    return empty_queue_list

# Printing Debug Functions
def PrintPhysicalSectors():
    for x in range(len(globals.physical_sectors)):
        print ("logical_addr = %s" % \
                globals.physical_sectors[x].logical_sector_addr)
        print ("physical_addr = %s" % \
                globals.physical_sectors[x].physical_sector_addr)
        print ("birth_time = %s" % globals.physical_sectors[x].birth_time)
        print ("death_time = %s" % globals.physical_sectors[x].death_time)
        print ("life_time = %s" % globals.physical_sectors[x].life_time)
        print ("\n")

def PrintAllocatedQueues():
    for x in range(len(globals.sectors)):
        print(globals.sectors[x].sector_addr, end="")
        print(": ", end="")
        for y in range(len(globals.sectors[x].queue_num)):
            print(globals.sectors[x].queue_num[y], end="")
            print(" ", end="")
        print("")

def PrintAllocatedQueuesChunks():
    for x in range(len(globals.chunks)):
        print(globals.chunks[x].chunk_addr, end="")
        print(": ", end="")
        for y in range(len(globals.chunks[x].queue_num)):
            print(globals.chunks[x].queue_num[y], end="")
            print(" ", end="")
        print("")

def PrintLogicalSectors():
    for x in range(len(globals.sectors)):
        print ("sector_addr = %s" % globals.sectors[x].sector_addr)
        print ("operation_times = %s" % globals.sectors[x].operation_times)
        print ("operations = %s" % globals.sectors[x].operation_type)
        print ("life_times = %s" % globals.sectors[x].life_times)
        print ("life_times_sizes = %s" % len(globals.sectors[x].life_times))
        print ("allocated_queues = %s" % globals.sectors[x].queue_num)
        print ("life_time_std_dev = %s" % globals.sectors[x].std_dev)

def PrintChunks():
    for x in range(len(globals.chunks)):
        print ("chunk_addr = %s" % globals.chunks[x].chunk_addr)
        print ("life_tuples = %s" % globals.chunks[x].life_tuples)
        print ("life_tuples_sizes = %s" % len(globals.chunks[x].life_tuples))
        print ("allocated_queues = %s" % globals.chunks[x].queue_num)

def PrintMetaInfo():
    print (globals.sector_size, globals.block_size, globals.sectors_per_block)
    print ("number of logical sectors = %s" % len(globals.sectors))
    print ("number of physical sectors = %s" % len(globals.physical_sectors))
    print ("number of max_time = %s" % globals.max_life_time)
    print ("number of min_time = %s" % globals.min_life_time)

