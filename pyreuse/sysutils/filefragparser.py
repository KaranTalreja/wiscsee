import os
import pprint

from pyreuse.helpers import run_and_get_output

def parse_file_frag_text(text):
    "text generated by filefrag -v"
    lines = text.split('\n')

    table = []
    for line in lines[3:-2]:
        d = _parse_line(line)
        table.append(d)

    return table

def _parse_line(line):
    items = line.split()
    items = [_clean_item(item) for item in items]

    keys = ['ext', 'logical_start', 'logical_end',
            'physical_start', 'physical_end', 'length',
            'expected', 'flags']

    if len(items) == 6:
        items.extend(['NA', 'NA'])
    elif len(items) == 7:
        items.extend(['NA'])

    d = dict(zip(keys, items))

    return d

def _clean_item(item):
    item = item.replace('.', '')
    item = item.replace(':', '')
    item = item.strip()

    # convert if we can
    try:
        item = int(item)
    except ValueError:
        pass

    return item

def parse_file_frag_file(path):
    with open(path, 'r') as f:
        text = f.read()

    return parse_file_frag_text(text)

def filefrag(filepath):
    lines = run_and_get_output('filefrag -v {}'.format(filepath))
    text = ''.join(lines)

    return parse_file_frag_text(text)

# TODO: this function should be moved somewhere else
def get_file_range_table(dirpath, BLOCKSIZE=4096):
    """
    Get a table:
    [
        {'path': '/mnt/fsonloop/appmix/0-Sqlite/data.db',
         'start_byte': 88237,
         'size':  4096},
        {'path': '/mnt/fsonloop/appmix/0-Sqlite/data.db',
         'start_byte': 882379,
         'size':  51200},
         ...
    ]
    """
    ret_table = []
    for root, dirs, files in os.walk(dirpath, topdown=False):
        for name in files:
            filepath = os.path.join(root, name)
            table = filefrag(filepath)
            file_range_table = file_range(table, filepath)
            ret_table.extend(file_range_table)

    return ret_table

def file_range(table, path, BLOCKSIZE=4096):
    """
    table is the thing you get from filefrag()
    """
    range_table = []

    for row in table:
        start_byte = row['physical_start'] * BLOCKSIZE
        size = row['length'] * BLOCKSIZE
        range_row = {'start_byte': start_byte,
                     'size': size,
                     'path': path}
        range_table.append(range_row)

    return range_table




