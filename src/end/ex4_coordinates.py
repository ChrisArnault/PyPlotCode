#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import matplotlib.pyplot as plt
import numpy as np
import library
import mylib

g_text = None
g_wcs = None
g_reg = None
g_fig = None

def move(event):

    global g_text

    if event.xdata is None or event.ydata is None:
        return

    x = int(event.xdata)
    y = int(event.ydata)

    ra, dec = library.convert_to_radec(g_wcs, x, y)

    results = g_reg.find_clusters(x, y, 5)

    ids = ['%s' % cl.cluster_id for cl in results]

    if g_text is not None:
        g_text.remove()
        g_text = None

    if len(results) > 0:

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

    file_name, batch = library.get_args()
    header, pixels = mylib.read_image(file_name)
    background, dispersion, _ = mylib.compute_background(pixels)

    # globals, for graphics
    global g_wcs, g_reg, g_text, g_fig

    # search for clusters in a sub-region of the image
    threshold = 6.0
    g_reg = mylib.Region(pixels, background + threshold*dispersion)
    g_reg.run_convolution()

    # coordinates ra dec
    max_cluster = g_reg.clusters[0]
    g_wcs = library.get_wcs(header)
    ra, dec = library.convert_to_radec(g_wcs, max_cluster['c'], max_cluster['r'])

    # console output
    print('right ascension: {:.3f}, declination: {:.3f}'.format(ra, dec))

    # graphic output
    if not batch:
        g_text = None
        g_fig, main_ax = plt.subplots()
        main_ax.imshow(g_reg.image)
        g_fig.canvas.mpl_connect('motion_notify_event', move)
        plt.show()

    return 0

if __name__ == '__main__':
    sys.exit(main())
