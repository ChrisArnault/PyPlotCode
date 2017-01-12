#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test program to
- open a fits files
- compute background of the sky image using a gaussian fit
- search for clusters
"""

import sys
import logging
from lib_args import get_args
import matplotlib.pyplot as plt
import lib_read_file
import lib_cluster
import lib_background

def main():

    '''
    Main function of the program
    '''

    file_name, header, pixels, batch = get_args('Exercise 3')
    if header is None:
        return 1

    logging.debug('name of image: %s', file_name)
    logging.debug('cd1_1: %s, cd1_2: %s, cd2_1: %s, cd2_2: %s',
                 header['CD1_1'], header['CD1_2'], header['CD2_1'], header['CD2_2'])
    logging.debug('height: %s, width: %s',
                 pixels.shape[0], pixels.shape[1])

    # compute background
    background, dispersion, _ = lib_background.compute_background(pixels)
    logging.debug('background: %s, dispersion: %s', int(background), int(dispersion))

    # search for clusters in a sub-region of the image
    threshold = 6.0
    """
    region[top:bottom, left:right]
    """
    top = 22 # 49
    bottom = 22 # 42
    left = 22 # 44
    right = 22 # 47

    top = 0
    bottom = 1
    left = 0
    right = 1

    logging.info('t=%d b=%d l=%d r=%d h=%d w=%d',
                 top, bottom,
                 left, right,
                 pixels.shape[0] - bottom - top, pixels.shape[1] - right - left)

    reg = lib_cluster.Region(pixels[top:-bottom, left:-right], background + threshold*dispersion)
    pattern, s, _ = reg.run_convolution()
    max_integral = reg.clusters[0]['integral']
    logging.info('number of clusters: %2d, greatest integral: %7d, centroid x: %4.1f, centroid y: %4.1f',
                 len(reg.clusters), max_integral, reg.clusters[0]['c'], reg.clusters[0]['r'])

    # graphic output

    if not batch:
        _, main_ax = plt.subplots(2)
        _ = main_ax[0].imshow(pattern)
        _ = main_ax[1].imshow(s)

        plt.show()

    return 0


if __name__ == '__main__':
    sys.exit(main())

