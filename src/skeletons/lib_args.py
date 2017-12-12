#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys, os, argparse


def get_args():

    # use argparse to analyse the command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', action="store_true", default=False, help='batch mode, no graphics and no interaction')
    parser.add_argument('file', nargs='?', help='fits input file')
    args = parser.parse_args()

    # establish the default path and file values
    DEFAULT_DATA_PATH = os.environ.get('DATAPATH')
    DEFAULT_DATA_FILE = 'NPAC'

    if DEFAULT_DATA_PATH == None:
        DEFAULT_DATA_PATH = '../data/fits'

    # if no file name given on the command line

    interactive = not args.b

    if not args.file:
        if not interactive:
            args.file = input('file name [%s]? ' % DEFAULT_DATA_FILE)
        if not interactive or len(args.file) == 0:
            args.file = DEFAULT_DATA_FILE

    file = DEFAULT_DATA_PATH + '/' + args.file + '.fits'

    return file, interactive


# =====
# Unit tests
# =====

if __name__ == '__main__':

    print(get_args())

    sys.exit(0)


