#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import matplotlib.pyplot as plt
import numpy as np
import library
import mylib

CONE = 0.001

def stars(region, wcs, fig):

    global g_all_stars
    g_all_stars = dict()

    for cluster in region.clusters:

        cobjects, _, _ = library.get_celestial_objects_from_pixels(cluster['c'], cluster['r'], wcs, CONE)

        for cobj in cobjects:
            if cobj not in g_all_stars:
                g_all_stars[cobj] = True
                print('STARS: ',cobj)
                plt.text(cluster['c'], cluster['r'], cobj, color='white')
       
        fig.canvas.draw()

class Mover():

    def __init__(self, the_wcs, the_fig):
        self.wcs = the_wcs
        self.fig = the_fig
        self.text = None

    def __call__(self, event):

        if event.xdata is None or event.ydata is None:
            return
        
        x = int(event.xdata)
        y = int(event.ydata)

        cobjects, _, _ = library.get_celestial_objects_from_pixels(x, y, self.wcs, CONE)

        if self.text is not None:
            self.text.remove()
            self.text = None

        for cobj in cobjects:
            print(('--------->', cobj))
            self.text = plt.text(x, y, '%s [%s, %s]' % (cobj, x, y), fontsize=14, color='red')
            print(('---------<', cobj))

        self.fig.canvas.draw()

def main():

    file_name, batch = library.get_args()
    header, pixels = mylib.read_image(file_name)
    background, dispersion, _ = mylib.compute_background(pixels)

    # search for clusters in a sub-region of the image
    threshold = 6.0
    region = mylib.Region(pixels, background + threshold*dispersion)
    pattern, cp_image, peaks = region.run_convolution()

    # coordinates ra dec
    max_cluster = region.clusters[0]
    wcs = library.get_wcs(header)
    ra, dec = library.convert_to_radec(wcs, max_cluster['c'], max_cluster['r'])

    # celestial objects
    cobjects, _, _ = library.get_celestial_objects_from_pixels(max_cluster['c'], max_cluster['r'], wcs, CONE)

    # console output
    for cobj in cobjects.keys():
        print('celestial object: {}'.format(cobj))

    # graphic output
    if not batch:
        fig, main_ax = plt.subplots()
        stars(region, wcs, fig)
        main_ax.imshow(peaks, interpolation='none')
        fig.canvas.mpl_connect('motion_notify_event',
          Mover(the_wcs=wcs,the_fig=fig))
        plt.show()

    return 0

if __name__ == '__main__':
    sys.exit(main())
