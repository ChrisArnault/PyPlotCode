#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
sys.path.append('../skeletons')
import matplotlib.pyplot as plt
import lib_args, lib_fits, lib_background, lib_cluster
import lib_wcs, lib_stars, lib_graphics


def get_celestial_objects( wcs, cluster ):

    pxy = lib_wcs.PixelXY(cluster.column, cluster.row)
    radec = lib_wcs.xy_to_radec(wcs, pxy)
    cobjects, _, _ = lib_stars.get_celestial_objects(radec)
    return cobjects


class ShowCelestialObjects():

    def __init__(self, wcs):

        self.wcs = wcs

    def __call__(self, cluster):

        return get_celestial_objects(self.wcs,cluster)


def main():

    file_name, interactive = lib_args.get_args()
    header, pixels = lib_fits.read_first_image(file_name)
    background, dispersion, _ = lib_background.compute_background(pixels)
    clustering = lib_cluster.Clustering()
    clusters = clustering(pixels, background, dispersion)

    # celestial objects for the biggest cluster
    wcs = lib_wcs.get_wcs(header)
    cobjects = get_celestial_objects(wcs, clusters[0])

    # console output
    for cobj in cobjects.keys():
        print('celestial object: {}'.format(cobj))

    # graphic output
    if interactive:
        fig, axis = plt.subplots()
        axis.imshow(pixels, interpolation='none')
        fig.canvas.mpl_connect('motion_notify_event',
            lib_graphics.ShowClusterProperties(fig,clusters,ShowCelestialObjects(wcs)))
        plt.show()

    return 0


if __name__ == '__main__':
    sys.exit(main())
