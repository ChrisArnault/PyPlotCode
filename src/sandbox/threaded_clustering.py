#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Test program to
- open a fits files
- compute background of the sky image using a gaussian fit
- search for clusters
"""


import sys ; sys.path.append('../skeletons')
import argparse
import matplotlib.pyplot as plt
import numpy as np
from lib_logging import logging
import lib_fits, lib_background, lib_cluster_thr, lib_args

DATAPATH = 'data/student/'
DATAFILE = 'NPAC'

reg = None


def main():

    '''
    Main function of the program
    '''

    global reg

    # process command-line options
    file_name, interactive = lib_args.get_args()
    header, pixels = lib_fits.read_first_image(file_name)

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
    if interactive:
        image = pixels

        reg = lib_cluster_thr.RegionThr(image, background + threshold*dispersion)
        reg.run_threaded()

        max_integral = reg.clusters[0].integral
        logging.info('number of clusters: %2d, greatest integral: %7d, centroid x: %4.1f, centroid y: %4.1f',
                     len(reg.clusters), max_integral, reg.clusters[0].centroid[1], reg.clusters[0].centroid[0])

        plt.show()

    return 0


if __name__ == '__main__':
    sys.exit(main())

