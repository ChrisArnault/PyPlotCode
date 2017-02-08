#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, time
import numpy as np
import matplotlib.pyplot as plt
import lib_args, lib_fits, lib_background
import lib_cluster, lib_pixels_set
sys.path.append('../skeletons')



# Main program

def main():

    file_name, batch = lib_args.get_args()
    header, pixels = lib_fits.read_first_image(file_name)
    background, dispersion, _ = lib_background.compute_background(pixels)

    # search for clusters
    clustering = Clustering()
    clusters = clustering.convolution_clustering(pixels, background, dispersion)
    max_cluster = clusters[0]

    # search for clusters in a sub-region of the image
    threshold = 6.0
    reg = lib_cluster.Region(pixels, background + threshold*dispersion)
    reg.run()

    # console output
    print('number of clusters: {:2d}, greatest integral: {:7d}, x: {:4.1f}, y: {:4.1f}'.format(
        len(clusters), max_cluster.integral, max_cluster.column, max_cluster.row))
    print('clustering execution time: {:.3f} seconds'.format(time1-time0))


    # graphic output
    if not batch:
        _, axis = plt.subplots()
        axis.imshow(lib_cluster.add_crosses(pixels, clusters))
        plt.show()

    return 0



if __name__ == '__main__':
    sys.exit(main())

