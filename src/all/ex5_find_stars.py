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
import lib_args
import lib_read_file
import lib_cluster
import lib_background
import lib_wcs as lwcs

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
class StarScan(object):

    'TODO : whatis it ?'

    def __init__(self, cluster, wcs, fig):
        'TODO : whatis it ?'
        #threading.Thread.__init__(self)
        self.cluster = cluster
        self.wcs = wcs
        self.fig = fig

    def run(self):
        'TODO : whatis it ?'

        # FIXME: update when using the new centroid definition
        y, x = self.cluster['r'], self.cluster['c']

        #g_io_lock.acquire()
        cobjects, _, _ = lwcs.get_celestial_objects_from_pixels(x, y, self.wcs, CONE)
        #g_io_lock.release()

        if len(cobjects) == 0:
            return

        for cobj in cobjects:
            if cobj not in g_all_stars:
                g_all_stars[cobj] = True

                #g_plt_lock.acquire()
                plt.text(x, y, cobj, color='white')
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


g_text = None
g_wcs = None
g_fig = None

def move_ex4(event):
    'TO BE DONE: What is it for ?'

    global g_text

    if event.xdata is None or event.ydata is None:
        return

    x = int(event.xdata)
    y = int(event.ydata)

    ra, dec = lwcs.convert_to_radec(g_wcs, x, y)

    results = g_reg.find_clusters(x, y, 5)

    if g_text is not None:
        g_text.remove()
        g_text = None

    if len(results) > 0:

        # logging.info('----------------x=%f y=%f RA=%f DEC=%f', x, y, ra - g_ra0, dec - g_dec0)

        # g_text = plt.text(x, y, '', fontsize=14, color='white')
        # g_fig.canvas.draw()

        for cluster in results:
            x = cluster['c']
            y = cluster['r']
            logging.info('x, y: %f, %f', x, y)
    else:
        g_fig.canvas.draw()

def move(event):

    'connect to the mouse motion event to try if a known star is around'

    global g_text

    if event.xdata is None or event.ydata is None:
        return

    x = int(event.xdata) + DX
    y = int(event.ydata) + DY

    print(x - DX, y - DY, x, y)

    cobjects, _, _ = lwcs.get_celestial_objects_from_pixels(x, y, g_wcs, CONE)

    if g_text is not None:
        g_text.remove()
        g_text = None

    for cobj in cobjects:
        print(('--------->', cobj))
        g_text = plt.text(x, y, '%s [%s, %s]' % (cobj, x, y), fontsize=14, color='red')
        print(('---------<', cobj))

    g_fig.canvas.draw()


def main():

    '''
    Main function of the program
    '''

    # step 1 : read file
    file_name, batch = lib_args.interpret_args()
    header, pixels = lib_read_file.read_first_image(file_name)
    if header is None:
        return 1
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

    reg = lib_cluster.Region(pixels[DY:ly, DX:lx], background + threshold*dispersion)
    pattern, cp_image, peaks = reg.run_convolution()
    max_integral = reg.clusters[0]['integral']
    
    logging.info('number of clusters: %2d, greatest integral: %7d, centroid x: %4.1f, centroid y: %4.1f',
                 len(reg.clusters), max_integral, reg.clusters[0]['c'], reg.clusters[0]['r'])

    for nc, ic in enumerate(reg.clusters):
        logging.info('cluster {} {} {} {} {} {}'.format( nc, ic['r'], ic['c'], ic['integral'], ic['top'], ic['radius']))

    # globals, for graphics
    global g_wcs, g_text, g_fig

    # coordinates
    centroid = (DY + reg.clusters[0]['r'], DX + reg.clusters[0]['c'])
    g_wcs = lwcs.get_wcs(header)
    g_ra, g_dec = lwcs.convert_to_radec(g_wcs, centroid[1], centroid[0])
    logging.info('right ascension: %.3f, declination: %.3f',g_ra, g_dec)

    # celestial objects
    #for nic, ic in enumerate(reg.clusters):
    ic = reg.clusters[0]
    r = DY + ic['r']
    c = DX + ic['c']
    # cobjects, _, _ = lwcs.get_celestial_objects_from_pixels(centroid[1], centroid[0], g_wcs, CONE)
    cobjects, _, _ = lwcs.get_celestial_objects_from_pixels(c, r, g_wcs, CONE)
    for cobj in list(cobjects.items()):
        logging.info('celestial object: %s', cobj[0])
        #logging.info('%d> celestial object: %s %s', nic, cobj[0], cobj[1])

    # graphics
    if not batch:
        g_text = None
        g_fig, main_ax = plt.subplots()
        stars(reg, g_wcs, g_fig)
        main_ax.imshow(peaks, interpolation='none')
        g_fig.canvas.mpl_connect('motion_notify_event', move)
        plt.show()

    return 0


if __name__ == '__main__':
    sys.exit(main())


