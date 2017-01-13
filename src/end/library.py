#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, argparse

DATAPATH = '../../data/fits/'
DATAFILE = 'NPAC'

def get_args():
    parser = argparse.ArgumentParser()
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

    return args.file, args.b

