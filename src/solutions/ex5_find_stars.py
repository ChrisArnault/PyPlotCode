#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import matplotlib.pyplot as plt
import numpy as np
import lib_args, lib_fits, lib_background, lib_cluster
import lib_wcs, lib_stars

CONE = 0.001


class ShowCelestialObjects():

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

                pxy = lib_wcs.PixelXY(cluster.column, cluster.row)
                radec = lib_wcs.xy_to_radec(self.wcs, pxy)

                cobjects, _, _ = lib_stars.get_celestial_objects(radec, CONE)
                tokens.extend(cobjects)

            self.text = plt.text(pxy.x, pxy.y, ' '.join(tokens), fontsize=14, color='white')

        self.fig.canvas.draw()


def main():

    file_name, batch = lib_args.get_args()
    header, pixels = lib_fits.read_first_image(file_name)
    background, dispersion, _ = lib_background.compute_background(pixels)

    # search for clusters
    clusters = lib_cluster.convolution_clustering(pixels, background + 6.0*dispersion)
    max_cluster = clusters[0]

    # coordinates ra dec
    wcs = lib_wcs.get_wcs(header)
    pxy = lib_wcs.PixelXY(max_cluster.column, max_cluster.row)
    radec = lib_wcs.xy_to_radec(wcs, pxy)

    # celestial objects
    cobjects, _, _ = lib_stars.get_celestial_objects(radec, CONE)

    # console output
    for cobj in cobjects.keys():
        print('celestial object: {}'.format(cobj))

    # graphic output
    if not batch:
        fig, main_ax = plt.subplots()
        main_ax.imshow(peaks, interpolation='none')
        fig.canvas.mpl_connect('motion_notify_event',
          ShowCelestialObjects(the_region=region,the_wcs=wcs,the_fig=fig))
        plt.show()

    return 0

if __name__ == '__main__':
    sys.exit(main())
