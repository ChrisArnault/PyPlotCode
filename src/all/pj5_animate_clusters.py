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
import lib_fits
import lib_cluster
import lib_background
import numpy as np
from matplotlib.widgets import RadioButtons
from matplotlib.widgets import Slider
from matplotlib.widgets import Button

DATAPATH = 'data/student/'
DATAFILE = 'NPAC'

reg = None
strategy = None
in_cluster = None
in_scanning = None


def main():

    '''
    Main function of the program
    '''

    global reg
    global strategy
    global in_cluster
    global in_scanning


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
    header,pixels = lib_fits.read_first_image(args.file)
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

        # cluster central
        image = pixels[45:70, 40:65]

        reg = lib_cluster.Region(image, background + threshold*dispersion)

        strategy = '4centers'
        in_cluster = 1.0
        in_scanning = 0.1

        def select_strategy(value):
            global strategy
            print(('select strategy=', value))
            strategy = value

        def select_in_cluster(value):
            global in_cluster
            in_cluster = value

        def select_in_scanning(value):
            global in_scanning
            in_scanning = value

        def start_animate(value):
            print(('animate with strategy=', strategy))
            reg.animate(in_cluster=in_cluster, in_scanning=in_scanning, strategy=strategy)

        strategies = ['random', 'all', 'center', '4centers']
        axis_strategy = plt.axes([0.2, 0.8, 0.15, 0.15])
        axis_strategy.set_title('Scanning strategy')
        strategy_widget = RadioButtons(axis_strategy, strategies)
        strategy_widget.set_active(strategies.index(strategy))
        strategy_widget.on_clicked(select_strategy)

        axis_in_cluster = plt.axes([0.2, 0.7, 0.65, 0.03])
        in_cluster_widget = Slider(axis_in_cluster, 'wait in clusters', 0.0, 5.0, valinit=in_cluster)
        in_cluster_widget.on_changed(select_in_cluster)

        axis_in_scanning = plt.axes([0.2, 0.6, 0.65, 0.03])
        in_scanning_widget = Slider(axis_in_scanning, 'wait in scanning', 0.0, 1.0, valinit=in_scanning)
        in_scanning_widget.on_changed(select_in_scanning)

        axis_animate = plt.axes([0.2, 0.5, 0.1, 0.03])
        in_animate = Button(axis_animate, 'Animate')
        in_animate.on_clicked(start_animate)

        plt.show()

    return 0


if __name__ == '__main__':
    sys.exit(main())

