#!/usr/bin/env python
# -*- coding: utf-8 -*-


from lib_config import sys
import matplotlib.pyplot as plt
import lib_args, lib_fits, lib_background, lib_cluster
import lib_wcs, lib_stars, lib_graphics
from lib_logging import logging


def get_celestial_objects( wcs, cluster ):

    pxy = lib_wcs.PixelXY(cluster.column, cluster.row)
    radec = lib_wcs.xy_to_radec(wcs, pxy)
    return lib_stars.get_celestial_objects(radec)


class ShowCelestialObjects():

    def __init__(self, wcs):
        self.wcs = wcs

    def __call__(self, cluster):
        return get_celestial_objects(self.wcs,cluster)


def main():

    # analyse command line arguments
    file_name, interactive = lib_args.get_args()
    logging.info('----------------')
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
    for icl, cl in enumerate(clusters):

        logging.info('----------------')
        logging.info('cluster {:d}: {}'.format(icl,cl))

        # radec coordinates of the greatest cluster
        wcs = lib_wcs.get_wcs(header)
        pxy = lib_wcs.PixelXY(cl.column, cl.row)
        radec = lib_wcs.xy_to_radec(wcs, pxy)
        logging.info('right ascension: {:.3f}'.format(radec.ra))
        logging.info('declination: {:.3f}'.format(radec.dec))

        # celestial objects for the biggest cluster
        cobjects, _, _ = get_celestial_objects(wcs, cl)
        for icobj, cobj in enumerate(cobjects.keys()):
            logging.info('celestial object {}: {}'.format(icobj,cobj))

    # graphic output
    if interactive:
        fig, axis = plt.subplots()
        axis.imshow(pixels, interpolation='none')
        fig.canvas.mpl_connect('motion_notify_event',
            lib_graphics.ShowClusterProperties(fig,clusters,ShowCelestialObjects(wcs)))
        plt.show()

    logging.info('----------------')
    return 0


if __name__ == '__main__':
    sys.exit(main())
