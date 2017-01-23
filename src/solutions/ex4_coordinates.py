#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys, logging
import numpy as np
import matplotlib.pyplot as plt
import lib_args, lib_fits, lib_background, lib_cluster
import lib_wcs


class ShowRaDec():

    def __init__(self, the_region, the_wcs, the_fig):

        self.region = the_region
        self.wcs = the_wcs
        self.fig = the_fig
        self.text = None

    def __call__(self, event):

        if event.xdata is None or event.ydata is None: return

        if self.text is not None:
            self.text.remove()
            self.text = None

        results = find_clusters(self.region.clusters,event.xdata,event.ydata, 5)

        if len(results) > 0:

            tokens = []
            for cluster in results:
                pxy = lib_wcs.PixelXY(cluster['c'], cluster['r'])
                radec = lib_wcs.xy_to_radec(self.wcs, pxy)
                tokens.append("{:.3f}/{d:.3f}".format(radec.ra, radec.dec))

            self.text = plt.text(pxy.x, pxy.y, ' '.join(tokens), fontsize=14, color='white')

        self.fig.canvas.draw()

def main():

    file_name, batch = lib_args.get_args()
    header, pixels = lib_fits.read_first_image(file_name)
    background, dispersion, _ = lib_background.compute_background(pixels)

    # search for clusters
    clusters = lib_cluster.convolution_clustering(pixels, background, dispersion)
    max_cluster = clusters[0]

    # coordinates ra dec
    wcs = lib_wcs.get_wcs(header)
    pxy = lib_wcs.PixelXY(max_cluster.column, max_cluster.row)
    radec = lib_wcs.xy_to_radec(wcs, pxy)

    # console output
    print('right ascension: {:.3f}, declination: {:.3f}'.format(radec.ra,radec.dec))

    # graphic output
    if not batch:
        fig, main_ax = plt.subplots()
        main_ax.imshow(pixels)
        fig.canvas.mpl_connect('motion_notify_event',
          ShowRaDec(the_region=region,the_wcs=wcs,the_fig=fig))
        plt.show()

    return 0

if __name__ == '__main__':
    sys.exit(main())
