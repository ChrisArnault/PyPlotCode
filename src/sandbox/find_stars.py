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
import lib_wcs, lib_stars

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

        pxy = lib_wcs.PixelXY(round(event.xdata),round(event.ydata))
        results = self.region.find_clusters(pxy.x, pxy.y, 5)

        print(pxy.x - DX, pxy.y - DY, pxy.x, pxy.y)

        radec = lib_wcs.xy_to_radec(self.wcs,xy)
        cobjects, _, _ = lib_stars.get_celestial_objects(radec, CONE)

        for cobj in cobjects:
            print(('--------->', cobj))
            self.text = plt.text(pxy.x, pxy.y, '%s [%s, %s]' % (cobj, pxy.x, pxy.y), fontsize=14, color='red')
            print(('---------<', cobj))

        self.fig.canvas.draw()


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
    threshold = 6.0

    lx = LX
    if lx == 0:
        lx = pixels.shape[0]

    ly = LY
    if ly == 0:
        ly = pixels.shape[1]

    region = lib_cluster.Region(pixels[DY:ly, DX:lx], background + threshold*dispersion)
    pattern, cp_image, peaks = region.run_convolution()
    max_integral = region.clusters[0]['integral']
    
    logging.info('number of clusters: %2d, greatest integral: %7d, centroid x: %4.1f, centroid y: %4.1f',
        len(region.clusters), max_integral, region.clusters[0]['c'], region.clusters[0]['r'])

    for nc, ic in enumerate(region.clusters):
        logging.info('cluster {} {} {} {} {} {}'.format( nc, ic['r'], ic['c'], ic['integral'], ic['top'], ic['radius']))

    # coordinates
    wcs = lib_wcs.get_wcs(header)
    pxy = lib_wcs.PixelXY(DX + region.clusters[0]['c'], DY + region.clusters[0]['r'])
    radec = lib_wcs.xy_to_radec(wcs, pxy)
    logging.info('right ascension: {:.3f}, declination: {:.3f}'.format(radec.ra, radec.dec))

    # celestial objects
    for nic, ic in enumerate(region.clusters):
        #ic = region.clusters[0]
        pxy = lib_wcs.PixelXY(DX + ic['c'], DY + ic['r'])
        radec = lib_wcs.xy_to_radec(wcs,pxy)
        cobjects, _, _ = lib_stars.get_celestial_objects(radec, CONE)
        for cobj in list(cobjects.items()):
            logging.info('%d> celestial object: %s %s', nic, cobj[0], cobj[1])

    # graphics
    if not batch:
        fig, main_ax = plt.subplots()
        stars(region, wcs, fig)
        main_ax.imshow(peaks, interpolation='none')
        g_fig.canvas.mpl_connect('motion_notify_event',
            ShowCelestialObjects(the_region=region,the_wcs=wcs,the_fig=fig))
        plt.show()

    return 0


if __name__ == '__main__':
    sys.exit(main())


