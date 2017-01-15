#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test program to
- open a fits files
- compute background of the sky image using a gaussian fit
- display the background analysis
- display the image
"""

import sys
from lib_logging import logging
from lib_args import get_args
import matplotlib.pyplot as plt
import lib_background


def main():

    '''
    Main function of the program
    '''

    file_name, header, pixels, batch = get_args('Exercise 2')
    if header is None:
        return 1


    logging.debug('name of image: %s', file_name)
    logging.debug('cd1_1: %s, cd1_2: %s, cd2_1: %s, cd2_2: %s',
                 header['CD1_1'], header['CD1_2'], header['CD2_1'], header['CD2_2'])
    logging.debug('height: %s, width: %s',
                 pixels.shape[0], pixels.shape[1])

    # compute background
    background, dispersion, _ = lib_background.compute_background(pixels)

    logging.info('background: %d, dispersion: %d' , int(background), int(dispersion))

    # graphic output
    if not batch:
        _, main_ax = plt.subplots()
        main_ax.imshow(pixels)
        plt.show()

    return 0


if __name__ == '__main__':
    sys.exit(main())

