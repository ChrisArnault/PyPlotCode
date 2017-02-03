#!/usr/bin/env python
# -*- coding: utf-8 -*-


import matplotlib.pyplot as plt
import lib_cluster


class ShowClusterProperties():

    def __init__(self, the_fig, the_clusters, the_func):

        self.clusters = the_clusters
        self.fig = the_fig
        self.func = the_func
        self.text = None

    def __call__(self, event):

        if event.xdata is None or event.ydata is None:
            return

        if self.text is not None:
            self.text.remove()
            self.text = None

        x, y = round(event.xdata), round(event.ydata)

        clusters = lib_cluster.find_clusters(self.clusters,y,x,5)

        if len(clusters) > 0:

            tokens = []
            for cluster in clusters:
                tokens.extend(self.func(cluster))
            label = ' '.join(tokens)
            self.text = plt.text(x,y,label,fontsize=14, color='white')

        self.fig.canvas.draw()


# =====
# Unit test
# =====

if __name__ == '__main__':

    import sys, lib_fits, lib_background, lib_wcs

    filename = '../../data/fits/NPAC.fits'
    header, pixels = lib_fits.read_first_image(filename)
    background, dispersion, _ = lib_background.compute_background(pixels)
    clusters = lib_cluster.convolution_clustering(pixels, background, dispersion)
    wcs = lib_wcs.get_wcs(header)

    fig, axis = plt.subplots()
    axis.imshow(pixels, interpolation='none')
    fig.canvas.mpl_connect('motion_notify_event',
        ShowClusterProperties(fig,clusters,lambda cl: [ "{}".format(cl.integral) ] ))
    plt.show()

    sys.exit(0)
