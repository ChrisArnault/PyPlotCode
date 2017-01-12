#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
import sys
import logging
import argparse

from lib_logging import logging
import lib_read_file

DATAPATH = 'data/student/'
DATAFILE = 'NPAC'

def get_args(title):
    parser = argparse.ArgumentParser(description=title)
    parser.add_argument('-b', action="store_true", default=False, \
                        help='batch mode, with no graphics and no interaction')
    parser.add_argument('file', nargs='?',
                        help='fits input file')
    args = parser.parse_args()
    if not args.file:
        if not args.b:
            args.file = input('file name [%s]? ' % DATAFILE)
        if args.b or len(args.file) == 0:
            args.file = DATAFILE
        args.file = DATAPATH + args.file + '.fits'

    # read image
    header = lib_read_file.read_header(args.file)
    pixels = lib_read_file.read_pixels(args.file)
    if pixels is None:
        return None, None, None

    return args.file, header, pixels, args.b


def tests():
    'Unit tests'
    return 0

if __name__ == '__main__':
    sys.exit(tests())


