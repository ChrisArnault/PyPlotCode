#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Test program to
- open a fits files
- compute background of the sky image using a gaussian fit
- display the background analysis
- display the image

pylint --extension-pkg-whitelist=numpy step2_background.py
"""

import sys
sys.path.append('../solutions')

import logging
from matplotlib.widgets import Slider
import matplotlib.pyplot as plt
import lib_args, lib_fits, lib_background
import numpy as np

pixels = None
imgplot = None
fig = None


def update_slider(val):

    global pixels
    global imgplot
    global fig

    threshold = s_thresh.val
    new_pixels = np.zeros_like(pixels)
    above = pixels >= threshold

    '''
    for r, row in enumerate(pixels):
        for c, col in enumerate(row):
            value = pixels[r, c]
            if above[r, c]:
                value = value - threshold
            else:
                value = 0

            new_pixels[r, c] = value
    '''

    new_pixels = pixels * above - above * threshold

    imgplot.set_data(new_pixels)
    fig.canvas.draw_idle()


def main():

    """The real main function"""
    global s_thresh
    global pixels
    global imgplot
    global fig

    logging.basicConfig(level=logging.DEBUG)

    file_name, batch = lib_args.get_args()
    header, pixels = lib_fits.read_first_image(file_name)
    background, dispersion, max_x = lib_background.compute_background(pixels)

    if not batch:
        
        fig, main_ax = plt.subplots()
        imgplot = main_ax.imshow(pixels)

        ax_thresh = plt.axes([0.25, 0.92, 0.65, 0.03])
        s_thresh = Slider(ax_thresh, 'Threshold', 0.0, max_x, valinit=background)

        s_thresh.on_changed(update_slider)
        update_slider(background)

        plt.show()


if __name__ == '__main__':
    main()


