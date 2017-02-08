#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Test program to
- open a fits files
- compute background of the sky image using a gaussian fit
- display the background analysis
- display the image
"""


import sys
from lib_logging import logging
import matplotlib.pyplot as plt
import lib_args, lib_fits, lib_background, lib_cluster
import lib_wcs, lib_stars, lib_graphics

CONE = 0.001
THREAD = False

DX = 0
LX = 0
DY = 0
LY = 0


"""
if THREAD:
    import threading
    g_io_lock = threading.Lock()
    g_plt_lock = threading.Lock()
else:
"""
g_io_lock = None
g_plt_lock = None

g_all_stars = dict()

# class StarScan(threading.Thread):
class StarScan():

    def __init__(self, cluster, wcs, fig):

        #threading.Thread.__init__(self)
        self.cluster = cluster
        self.wcs = wcs
        self.fig = fig

    def run(self):

        # FIXME: update when using the new centroid definition
        pxy = lib_wcs.PixelXY(self.cluster['c'], self.cluster['r'])

        #g_io_lock.acquire()
        radec = lib_wcs.xy_to_radec(self.wcs,pxy)
        cobjects, _, _ = lib_stars.get_celestial_objects(radec, CONE)
        #g_io_lock.release()

        if len(cobjects) == 0:
            return

        for cobj in cobjects:
            if cobj not in g_all_stars:
                g_all_stars[cobj] = True

                #g_plt_lock.acquire()
                plt.text(pxy.x, pxy.y, cobj, color='white')
                self.fig.canvas.draw()
                #g_plt_lock.release()


def stars(region, wcs, fig):

    '''
    Check for all found clusters if a known star exists at its position.
    Several clusters may be associated with the same star : g_all_stars
    is used to avoid duplicates.
    :param region:
    :param wcs:
    :param fig:
    :return:
    '''

    global g_all_stars
    g_all_stars = dict()

    for cluster in region.clusters:
        thr = StarScan(cluster, wcs, fig)
        #thr.start()
        thr.run()
        break


class ShowCelestialObjects():

    def __init__(self, wcs):

        self.wcs = wcs

    def __call__(self, cluster):

        pxy = lib_wcs.PixelXY(cluster.column,cluster.row)
        radec = lib_wcs.xy_to_radec(self.wcs,pxy)
        cobjects, _, _ = lib_stars.get_celestial_objects(radec, CONE)
        result = []
        for cobj in cobjects:
            result.append('{} [{}, {}]'.format(cobj, pxy.x, pxy.y))
        return result


def main():

    '''
    Main function of the program
    '''

    # step 1 : read file
    file_name, batch = lib_args.get_args()
    header, pixels = lib_fits.read_first_image(file_name)
    logging.info('name of image: %s', file_name)
    logging.info('cd1_1: %s, cd1_2: %s, cd2_1: %s, cd2_2: %s',
        header['CD1_1'], header['CD1_2'], header['CD2_1'], header['CD2_2'])
    logging.info('height: %s, width: %s', pixels.shape[0], pixels.shape[1])

    # step 2 : compute background
    background, dispersion, _ = lib_background.compute_background(pixels)
    logging.info('background: %s, dispersion: %s', int(background), int(dispersion))

    # search for clusters in a sub-region of the image

    lx = LX
    if lx == 0:
        lx = pixels.shape[0]

    ly = LY
    if ly == 0:
        ly = pixels.shape[1]

    clustering = lib_cluster.Clustering()
    clusters = clustering.convolution_clustering(pixels[DY:ly, DX:lx], background, dispersion)
    cluster0 = clusters[0]
    max_integral = cluster0.integral
    
    logging.info('number of clusters: %2d, greatest integral: %7d, x: %4.1f, y: %4.1f',
        len(clusters), max_integral, cluster0.column, cluster0.row)

    for nc, ic in enumerate(clusters):
        logging.info('cluster {}: {}'.format( nc, ic))

    # coordinates
    wcs = lib_wcs.get_wcs(header)
    pxy = lib_wcs.PixelXY(DX + cluster0.column, DY + cluster0.row)
    radec = lib_wcs.xy_to_radec(wcs, pxy)
    logging.info('right ascension: {:.3f}, declination: {:.3f}'.format(radec.ra, radec.dec))

    # celestial objects
    for nic, ic in enumerate(clusters):
        #ic = region.clusters[0]
        pxy = lib_wcs.PixelXY(DX + ic.column, DY + ic.row)
        radec = lib_wcs.xy_to_radec(wcs,pxy)
        cobjects, _, _ = lib_stars.get_celestial_objects(radec, CONE)
        for cobj in sorted(list(cobjects.keys())):
            logging.info('%d> celestial object: %s %s', nic, cobj, cobjects[cobj])

    # graphics
    if not batch:
        fig, axis = plt.subplots()
        #stars(region, wcs, fig)
        axis.imshow(lib_cluster.add_crosses(pixels,clusters), interpolation='none')
        fig.canvas.mpl_connect('motion_notify_event',
            lib_graphics.ShowClusterProperties(fig,clusters,ShowCelestialObjects(wcs)))
        plt.show()

    return 0


if __name__ == '__main__':
    sys.exit(main())


