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

if __name__ == '__main__':

    # test_Simbad
    objects = get_objects(1.0, 1.0, 0.1)
    for object in objects:
        print('{} ({})'.format(object, objects[object]))
    if len(objects) != 14:
        print('error')

    # test_WCS

    header = None
    try:
        with fits.open('../data/dss.19.59.54.3+09.59.20.9 10x10.fits') as data_fits:
            try:
                data_fits.verify('silentfix')
                header = data_fits[0].header
            except ValueError as err:
                logging.error('Error: %s', err)
    except EnvironmentError as err:
        logging.error('Cannot open the data fits file. - %s', err)

    w = WCS(header)
    ra, dec = w.convert_to_radec(0, 0)

    print(ra, dec)

    if abs(ra - 300.060983768) > 1e-5:
        print('error')

    if abs(dec - 9.90624639801) > 1e5:
        print('error')
