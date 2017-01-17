#!/usr/bin/env python
# -*- coding: utf-8 -*-

from matplotlib.widgets import Slider

from lib_read_file import *
from lib_cluster import *
from lib_background import *

"""
Test program to
- open a fits files
- compute background of the sky image using a gaussian fit
- display the background analysis
- display the image
"""

DATAFILES = 'data/student/NPAC.fits'

def main():
    logging.basicConfig(level=logging.DEBUG)

    header, pixels = lib_read_file.read_first_image(DATAFILES)

    # shape:
    #   first element=#rows (-> image height)
    #   second element=#columns (-> image width)

    background, dispersion, max_x = compute_background(pixels)

    # search for clusters in a sub-region of the image
    # we set a threshold

    threshold = 6.0
    r = Region(pixels, background + threshold*dispersion)
    r.run()

    logging.info('%d clusters', len(r.clusters))

    fig, main_ax = plt.subplots()
    imgplot = main_ax.imshow(r.image)

    axcolor = 'lightgoldenrodyellow'
    ax_thresh = plt.axes([0.25, 0.92, 0.65, 0.03], axisbg=axcolor)
    s_thresh = Slider(ax_thresh, 'Threshold', 0.0, 30.0, valinit=threshold)

    def update(val):
        threshold = s_thresh.val
        print(background, threshold, dispersion, background + threshold*dispersion)
        r.run(background + threshold*dispersion)
        logging.info('%d clusters', len(r.clusters))

        imgplot.set_data(r.image)
        fig.canvas.draw_idle()

    s_thresh.on_changed(update)

    plt.show()


if __name__ == '__main__':
    main()
