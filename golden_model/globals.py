#! /usr/bin/python3

# See LICENSE for license details.

import sys
import getopt
import math

######################### Global Variable Defines ##############################
physical_sectors = []
sectors = []
input_file = ''
sector_size = 512
block_size = 4096
total_size = 2^30
queue_entries = 8
sectors_per_block = block_size/sector_size

def init():
    global physical_sector
    global sectors
    global input_file
    global sector_size
    global block_size
    global total_size
    global queue_entries
    global sectors_per_block

