#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
sys.path.append('../skeletons')
import lib_args, lib_fits, lib_background, lib_cluster
import lib_wcs, lib_graphics


class ShowRaDec():

    def __init__(self, wcs):

        self.wcs = wcs

    def __call__(self, cluster):

        pxy = lib_wcs.PixelXY(cluster.column, cluster.row)
        radec = lib_wcs.xy_to_radec(self.wcs, pxy)
        return [ "{:.3f}/{:.3f}".format(radec.ra, radec.dec) ]


def main():

    file_name, interactive = lib_args.get_args()
    header, pixels = lib_fits.read_first_image(file_name)
    background, dispersion, _ = lib_background.compute_background(pixels)
    clustering = lib_cluster.Clustering()
    clusters = clustering(pixels, background, dispersion)
    max_cluster = clusters[0]

    # coordinates ra dec
    wcs = lib_wcs.get_wcs(header)
    pxy = lib_wcs.PixelXY(max_cluster.column, max_cluster.row)
    radec = lib_wcs.xy_to_radec(wcs, pxy)

    # console output
    print('RESULT: right_ascension = {:.3f}'.format(radec.ra))
    print('RESULT: declination = {:.3f}'.format(radec.dec))

    # graphic output
    if interactive:
        import matplotlib.pyplot as plt

        fig, axis = plt.subplots()
        axis.imshow(pixels)
        fig.canvas.mpl_connect('motion_notify_event',
            lib_graphics.ShowClusterProperties(fig,clusters,ShowRaDec(wcs)))
        plt.show()

    return 0


if __name__ == '__main__':

    sys.exit(main())
