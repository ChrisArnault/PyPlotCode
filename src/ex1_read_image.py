#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Read and plot a fits image
See https://pythonhosted.org/pyfits/
"""

import sys
import logging
from lib_args import get_args
import matplotlib.pyplot as plt


def main():

    '''
    Main function of the program
    '''

    file_name, header, pixels, batch = get_args('Exercise 1')
    if header is None:
        return 1

    # command line outputgit
    # shape:
    #   first element=#rows (-> image height)
    #   second element=#columns (-> image width)
    logging.debug('name of image: %s', file_name)

    logging.info('cd1_1: %.10f, cd1_2: %.10f, cd2_1: %.10f, cd2_2: %.10f', header['CD1_1'], header['CD1_2'], header['CD2_1'], header['CD2_2'])

    logging.debug('height: %s, width: %s',
                 pixels.shape[0], pixels.shape[1])

    # graphic output
    if not batch:
        _, main_ax = plt.subplots()
        plt.text(0, -10, file_name, fontsize=14, color='white')
        main_ax.imshow(pixels)
        plt.show()

    return 0


if __name__ == '__main__':
    sys.exit(main())

