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
        self.std_dev = 0

# Info for each physical sector
class PhysicalSectorInfo():

    def __init__(self):
        self.logical_sector_addr = 0
        self.physical_sector_addr = 0
        self.birth_time = 0
        self.death_time = 0
        self.life_time = 0

############################# Function Defines #################################

# Function for sorting physical sectors based on the creation time
def UpdateSectorsPerBlock():

    globals.sectors_per_block = globals.block_size/globals.sector_size

# Take the inputs
def GetArgs(argv):

    found_input_file = False

    try:
        opts, args = getopt.getopt(argv,"hi:s:b:t:q:",["ifile=", \
        "sector_size", "block_size", "total_size", "queue_entries"])
    except getopt.GetoptError:
        print ('ERROR: golden_model_gen.py')
        print ('    -i <globals.input_file>')
        print ('    -s <sector_size>')
        print ('    -b <block_size>')
        print ('    -t <total_size>')
        print ('    -q <queue_entries>')
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
            queue_entries = arg
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

    for logical_sector in range(len(globals.sectors)):
        for physical_sector in \
                range(len(globals.sectors[logical_sector].operation_times)):
            if globals.sectors[logical_sector].operation_type[physical_sector]\
                    == 'write':
                globals.physical_sectors.append(PhysicalSectorInfo())
                globals.physical_sectors[-1].logical_sector_addr = \
                    globals.sectors[logical_sector].sector_addr
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
                if globals.physical_sectors[-1].death_time != math.inf:
                    globals.sectors[logical_sector].life_times.append(\
                        globals.physical_sectors[-1].death_time - \
                        globals.physical_sectors[-1].birth_time)

# Calculate standard deviation for all sectors
def CalculateStdDev():
    for logical_sector in range(len(globals.sectors)):
        globals.sectors[logical_sector].std_dev = \
                numpy.std(globals.sectors[logical_sector].life_times, \
                dtype=numpy.float64)

# Function for sorting physical sectors based on the creation time
def TimeSortingFunc(elem):
    return elem.birth_time

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

def PrintLogicalSectors():
    for x in range(len(globals.sectors)):
        print ("sector_addr = %s" % globals.sectors[x].sector_addr)
        print ("operation_times = %s" % globals.sectors[x].operation_times)
        print ("operations = %s" % globals.sectors[x].operation_type)
        print ("life_times = %s" % globals.sectors[x].life_times)
        print ("life_time_std_dev = %s" % globals.sectors[x].std_dev)

def PrintMetaInfo():
    print (globals.sector_size, globals.block_size, globals.sectors_per_block)
    print ("number of logical sectors = %s" % len(globals.sectors))
    print ("number of physical sectors = %s" % len(globals.physical_sectors))

