#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test program to
- open a fits files
- compute background of the sky image using a gaussian fit
- search for clusters
"""

import sys
import argparse

import matplotlib.pyplot as plt

from lib_logging import logging
import lib_read_file
import lib_cluster
import lib_background
import numpy as np

DATAPATH = 'data/student/'
DATAFILE = 'NPAC'

reg = None


def main():

    '''
    Main function of the program
    '''

    global reg

    # process command-line options
    parser = argparse.ArgumentParser(description='Exercise 3')
    parser.add_argument('-b', action="store_true", default=False, \
        help='batch mode, with no graphics and no interaction')
    parser.add_argument('file', nargs='?',
                        help='fits input file')
    args = parser.parse_args()
    if not args.file:
        if not args.b:
            args.file = eval(input('file name [%s]? ' % DATAFILE))
        if args.b or len(args.file) == 0:
            args.file = DATAFILE
        args.file = DATAPATH + args.file + '.fits'

    # args.file = 'data/misc/dss.19.59.54.3+09.59.20.9_40x20.fits'
    # read image
    header = lib_read_file.read_header(args.file)
    pixels = lib_read_file.read_pixels(args.file)
    if pixels is None:
        return 1
    logging.debug('name of image: %s', args.file)
    logging.debug('cd1_1: %s, cd1_2: %s, cd2_1: %s, cd2_2: %s',
                 header['CD1_1'], header['CD1_2'], header['CD2_1'], header['CD2_2'])
    logging.debug('height: %s, width: %s',
                 pixels.shape[0], pixels.shape[1])

    # compute background
    background, dispersion, _ = lib_background.compute_background(pixels)
    logging.debug('background: %s, dispersion: %s', int(background), int(dispersion))

    print('---------------------')
    # search for clusters in a sub-region of the image
    threshold = 6.0

    # graphic output
    if not args.b:
        image = pixels

        reg = lib_cluster.Region(image, background + threshold*dispersion)
        reg.run_threaded()

        max_integral = reg.clusters[0].integral
        logging.info('number of clusters: %2d, greatest integral: %7d, centroid x: %4.1f, centroid y: %4.1f',
                     len(reg.clusters), max_integral, reg.clusters[0].centroid[1], reg.clusters[0].centroid[0])

        plt.show()

    return 0


if __name__ == '__main__':
    sys.exit(main())

