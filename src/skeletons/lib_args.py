#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys, os, argparse


def get_args():

    # use argparse to analyse the command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', dest="batch", action="store_true", default=False, help='batch mode, no graphics and no interaction')
    parser.add_argument('file', nargs='?', help='fits input file')
    args = parser.parse_args()

    if not args.file:
        # if no file name given on the command line
        DEFAULT_DATA_FILE = 'common'
        if args.batch:
            file = DEFAULT_DATA_FILE
        else:
            file = input('file name [%s]? ' % DEFAULT_DATA_FILE)
            if len(file) == 0:
                file = DEFAULT_DATA_FILE
    else:
        file = args.file

    if not file.endswith('.fits'):
        # we need *.fits files
        file += '.fits'

    if file.rfind('/') == -1 and file.rfind('\\') == -1:
        # when an explicit path is not provided, prepend the default path
        # other wise don't touch it
        # establish the default path and file values
        DEFAULT_DATA_PATH = os.environ.get('DATAPATH')
        if DEFAULT_DATA_PATH == None:
            if os.path.exists('../../data/fits'):
                DEFAULT_DATA_PATH = '../../data/fits'
            elif os.path.exists('../data/fits'):
                DEFAULT_DATA_PATH = '../data/fits'
            elif os.path.exists('../data'):
                DEFAULT_DATA_PATH = '../data'
            else:
                print('No default data path found', file=sys.stderr)
                exit(1)

        file = DEFAULT_DATA_PATH + '/' + file

    if not os.path.exists(file):
        raise FileNotFoundError('Image file ({}) not found'.format(file))

    # we don't test if the file actually exists.
    # thus we expect that this test will occur at open time (perhaps using a try clause)

    return file, not args.batch


# =====
# Unit tests
# =====

if __name__ == '__main__':

    print(get_args())

    sys.exit(0)


