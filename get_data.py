"""
This module deals with parsing datapoints out of logfiles. They are then
finally provided as a dict (`datadict`) for further processing.


NOTE:
A filename is expected to look like 'L1234567.890', where the
first character is one of (L,C,S) indicating the status of the file,
and the rest consists of a funny 10-digit timestamp.

"""
import logging
import os
import re

from collections import defaultdict
from datetime import datetime

# A datapoint is everything in brackets without the brackets
DP_REGEX = '(?<=\()[^\)]+'

def last_files(dir_path, regex_filter, n, sort_func=None):
    """
    Returns the last `n` filenames in `dir_path` that match a `regex_filter`,
    sorted by their name.
    If provided, a sort function `sort_func` is passed as key to the sorted
    function.
    """
    filenames = sorted([f for f in os.listdir(dir_path)
                        if re.match(regex_filter, f)],
    		       key=sort_func)[-n:]
    return [os.path.join(dir_path, f) for f in filenames]

def validate_datapoint(datapoint):
    """
    Assure it has 3 or more parts (name, ts, value(s))
    """
    items = datapoint.split(' ')
    return len(items) >= 3


def get_datapoints(filename):
    with open(filename) as f: # ensures full file handling (closing, ..)
        for dp in (dps for l in f for dps in re.findall(DP_REGEX, l)):
            if validate_datapoint(dp):
                yield dp
            else:
                logging.error("invalid datapoint: " + dp)

def datadict(filenames):
    points = defaultdict(lambda: defaultdict(list))
    for dp in (dps for f in filenames for dps in get_datapoints(f)):
        items = dp.split(" ")
        name, ts, vv = items[0], items[1], items[2:]
        points[name]['time'].append(ts)
        for i, v in enumerate(vv):
            points[name]['line_%s' % i].append(v)
    return points


if __name__ == '__main__':
    dir_path = '/mnt/sda1' # typical filepath on a Arduino YUN
    # we want to sort on the timestamps
    sort_func = lambda s: s[1:]
    print(datadict(last_files(dir_path, '^[CL]', 5, sort_func)))
