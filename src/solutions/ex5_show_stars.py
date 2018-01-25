#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
sys.path.append('../skeletons')
import lib_args, lib_fits, lib_background, lib_cluster
import lib_wcs
import lib_stars


def get_celestial_objects( wcs, cluster ):
    pxy = lib_wcs.PixelXY(cluster.column, cluster.row)
    radec = lib_wcs.xy_to_radec(wcs, pxy)
    return lib_stars.get_celestial_objects(radec)

def show_cluster(wcs, i, cluster):
    print('DEBUG: {} cluster={} {} {}'.format(i, cluster.integral, cluster.column, cluster.row))

    pxy = lib_wcs.PixelXY(cluster.column, cluster.row)
    radec = lib_wcs.xy_to_radec(wcs, pxy)

    print('RESULT: right_ascension_{:d} = {:.3f}'.format(i,radec.ra))
    print('RESULT: declination_{:d} = {:.3f}'.format(i,radec.dec))

    os, _, _ = get_celestial_objects(wcs, cluster)
    for cobj in os.keys():
        print('RESULT: celestial_object_{:d} = {}'.format(i,cobj))


class ShowRaDec():

    def __init__(self, wcs):

        self.wcs = wcs

    def __call__(self, cluster):

        pxy = lib_wcs.PixelXY(cluster.column, cluster.row)
        radec = lib_wcs.xy_to_radec(self.wcs, pxy)
        return [ "{:.3f}/{:.3f}".format(radec.ra, radec.dec) ]


class ShowCelestialObjects():

    def __init__(self, wcs):
        self.wcs = wcs

    def __call__(self, cluster):
        pxy = lib_wcs.PixelXY(cluster.column, cluster.row)
        radec = lib_wcs.xy_to_radec(self.wcs, pxy)
        obj, _, _ = get_celestial_objects(self.wcs, cluster)
        return [ "{:.3f}/{:.3f} {}".format(radec.ra, radec.dec, obj) ]


def main():

    file_name, interactive = lib_args.get_args()
    header, pixels = lib_fits.read_first_image(file_name)
    background, dispersion, _ = lib_background.compute_background(pixels)
    clustering = lib_cluster.Clustering()
    clusters = clustering(pixels, background, dispersion)
    max_cluster = clusters[0]

    # coordinates ra dec
    wcs = lib_wcs.get_wcs(header)

    for i, c in enumerate(clusters):
        show_cluster(wcs, i, c)

    # graphic output
    if interactive:
        import matplotlib.pyplot as plt
        import lib_graphics

        fig, axis = plt.subplots()
        axis.imshow(pixels, interpolation='none')
        fig.canvas.mpl_connect('motion_notify_event',
            lib_graphics.ShowClusterProperties(fig,clusters,ShowCelestialObjects(wcs)))
        plt.show()

    return 0


if __name__ == '__main__':

    sys.exit(main())
