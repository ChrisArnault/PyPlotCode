#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import matplotlib.pyplot as plt
import numpy as np
import library
import mylib
import logging

class Mover():

    def __init__(self, the_region, the_wcs, the_fig):
        self.region = the_region
        self.wcs = the_wcs
        self.fig = the_fig
        self.text = None

    def __call__(self, event):

        if event.xdata is None or event.ydata is None:
            return
        
        x = int(event.xdata)
        y = int(event.ydata)

        ra, dec = library.convert_to_radec(self.wcs, x, y)

        results = self.region.find_clusters(x, y, 5)
        # print('region:',self.region.cluster_coords)

        # ids = ['%s' % cl.cluster_id for cl in results]
        # print(x,y,':',ids)

        if self.text is not None:
            self.text.remove()
            self.text = None

        if len(results) > 0:

            # self.text = plt.text(x, y, '', fontsize=14, color='white')
            # self.fig.canvas.draw()

            for cluster in results:
                x = cluster['c']
                y = cluster['r']
                print('found: x, y:', x, y)
        else:
            self.fig.canvas.draw()

def main():

    file_name, batch = library.get_args()
    header, pixels = mylib.read_image(file_name)
    background, dispersion, _ = mylib.compute_background(pixels)

    # globals, for graphics
    global g_wcs, g_reg, g_text, g_fig

    # search for clusters in a sub-region of the image
    threshold = 6.0
    region = mylib.Region(pixels, background + threshold*dispersion)
    region.run_convolution()

    # coordinates ra dec
    max_cluster = region.clusters[0]
    wcs = library.get_wcs(header)
    ra, dec = library.convert_to_radec(wcs, max_cluster['c'], max_cluster['r'])

    # console output
    print('right ascension: {:.3f}, declination: {:.3f}'.format(ra, dec))

    # graphic output
    if not batch:
        fig, main_ax = plt.subplots()
        main_ax.imshow(region.image)
        fig.canvas.mpl_connect('motion_notify_event',
          Mover(the_region=region,the_wcs=wcs,the_fig=fig))
        plt.show()

    return 0

if __name__ == '__main__':
    sys.exit(main())
