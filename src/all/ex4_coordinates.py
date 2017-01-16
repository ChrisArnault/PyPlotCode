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

import lib_read_file
import lib_cluster
import lib_background
import lib_wcs as lwcs

g_text = None
g_wcs = None
g_reg = None
g_ra0 = None
g_dec0 = None
g_fig = None

def move(event):
    'TO BE DONE: What is it for ?'

    global g_text

    if event.xdata is None or event.ydata is None:
        return

    x = int(event.xdata)
    y = int(event.ydata)

    ra, dec = lwcs.convert_to_radec(g_wcs, x, y)

    results = g_reg.find_clusters(x, y, 5)

    ids = ['%s' % cl.cluster_id for cl in results]

    # logging.info('ids=%s', repr(ids))

    if g_text is not None:
        g_text.remove()
        g_text = None

    if len(results) > 0:

        # logging.info('----------------x=%f y=%f RA=%f DEC=%f', x, y, ra - g_ra0, dec - g_dec0)

        g_text = plt.text(x, y, '\n'.join(ids), fontsize=14, color='white')
        g_fig.canvas.draw()

        for cluster in results:
            centroid = cluster.centroid
            x = centroid.c
            y = centroid.r
            logging.info('x, y: %f, %f', x, y)
    else:
        g_fig.canvas.draw()


def main():

    '''
    Main function of the program
    '''

    file_name, header, pixels, batch = get_args('Exercise 4')
    if header is None:
        return 1

    # globals, for graphics
    global g_wcs, g_reg, g_ra0, g_dec0, g_text, g_fig

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
    g_reg = lib_cluster.Region(pixels, background + threshold*dispersion)
    g_reg.run_convolution()
    max_integral = g_reg.clusters[0]['integral']
    logging.debug('nb clusters: %s, greatest integral: %s',len(g_reg.clusters), max_integral)

    # coordinates
    centroid = (g_reg.clusters[0]['r'], g_reg.clusters[0]['c'])
    g_wcs = lwcs.get_wcs(header)
    g_ra, g_dec = lwcs.convert_to_radec(g_wcs, centroid[1], centroid[0])
    logging.info('right ascension: %.3f, declination: %.3f', g_ra, g_dec)

    # graphics
    if not batch:
        g_text = None
        g_fig, main_ax = plt.subplots()
        main_ax.imshow(g_reg.image)
        g_fig.canvas.mpl_connect('motion_notify_event', move)
        plt.show()

    return 0


if __name__ == '__main__':
    sys.exit(main())

