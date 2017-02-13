#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
sys.path.append('../skeletons')
sys.path.append('../solutions')

import matplotlib.pyplot as plt
import lib_args, lib_fits, lib_background, lib_cluster
import lib_wcs, lib_stars, lib_graphics
from lib_logging import logging


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

    # analyse command line arguments
    file_name, batch = lib_args.get_args()
    logging.info('name of file: {}'.format(file_name))

    # read fits file
    header, pixels = lib_fits.read_first_image(file_name)
    logging.info('cd1_1: {CD1_1:.10f}'.format(**header))
    logging.info('cd1_2: {CD1_2:.10f}'.format(**header))
    logging.info('cd2_1: {CD2_1:.10f}'.format(**header))
    logging.info('cd2_2: {CD2_2:.10f}'.format(**header))

    # compute background
    background, dispersion, _ = lib_background.compute_background(pixels)
    logging.info('background: {:d}'.format(int(background)))
    logging.info('dispersion: {:d}'.format(int(dispersion)))

    # clustering
    clustering = lib_cluster.Clustering()
    clusters = clustering(pixels, background, dispersion)
    logging.info('number of clusters: {:2d}'.format(len(clusters)))
    logging.info('greatest integral: {}'.format(clusters[0]))

    # radec coordinates of the greatest cluster
    wcs = lib_wcs.get_wcs(header)
    pxy = lib_wcs.PixelXY(clusters[0].column, clusters[0].row)
    radec = lib_wcs.xy_to_radec(wcs, pxy)
    logging.info('right ascension: {:.3f}'.format(radec.ra))
    logging.info('declination: {:.3f}'.format(radec.dec))

    # celestial objects for the biggest cluster
    cobjects = get_celestial_objects(wcs, clusters[0])
    for cobj in cobjects.keys():
        logging.info('celestial object: {}'.format(cobj))

    # graphic output
    if not batch:
        fig, axis = plt.subplots()
        axis.imshow(pixels, interpolation='none')
        fig.canvas.mpl_connect('motion_notify_event',
            lib_graphics.ShowClusterProperties(fig,clusters,ShowCelestialObjects(wcs)))
        plt.show()

    return 0


if __name__ == '__main__':
    sys.exit(main())
