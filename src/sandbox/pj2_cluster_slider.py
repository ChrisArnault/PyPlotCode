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
sys.path.append('../solutions')

import matplotlib.pyplot as plt
from lib_logging import logging
from matplotlib.widgets import Slider
import lib_args, lib_fits, lib_background, lib_cluster 


def main():

    file_name, batch = lib_args.get_args()
    header, pixels = lib_fits.read_first_image(file_name)

    # shape:
    #   first element=#rows (-> image height)
    #   second element=#columns (-> image width)

    background, dispersion, max_x = lib_background.compute_background(pixels)

    # search for clusters in a sub-region of the image
    # we set a threshold
    threshold = 6.0
    clusters = lib_cluster.convolution_clustering(pixels, background + threshold*dispersion)
    logging.info('%d clusters', len(clusters))

    if not batch:
        
        fig, main_ax = plt.subplots()
        imgplot = main_ax.imshow(pixels)

        axcolor = 'lightgoldenrodyellow'
        ax_thresh = plt.axes([0.25, 0.92, 0.65, 0.03], axisbg=axcolor)

        x = background + threshold*dispersion
        s_thresh = Slider(ax_thresh, 'Threshold', 0.0, 5 * x, valinit=x)

        def update(val):

            x = s_thresh.val
            print(background, threshold, dispersion, x)
            clusters = lib_cluster.convolution_clustering(pixels, x)
            peaks = add_crosses(pixels,clusters)
            logging.info('%d clusters', len(clusters))

            imgplot.set_data(peaks)
            fig.canvas.draw_idle()

        s_thresh.on_changed(update)

        plt.show()


if __name__ == '__main__':
    main()
