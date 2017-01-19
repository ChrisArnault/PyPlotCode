#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import matplotlib.pyplot as plt
import numpy as np
import lib_args, lib_fits, lib_background, lib_cluster


def main():

    file_name, batch = lib_args.get_args()
    header, pixels = lib_fits.read_first_image(file_name)
    background, dispersion, _ = lib_background.compute_background(pixels)

    # search for clusters
    region = lib_cluster.Region(pixels, background + 6.0*dispersion)
    pattern, s, _ = region.run_convolution()
    max_cluster = region.clusters[0]
    max_integral = max_cluster['integral']

    # console output
    print('number of clusters: {:2d}, greatest integral: {:7d}, centroid x: {:4.1f}, centroid y: {:4.1f}'.format(
        len(region.clusters), max_integral, max_cluster['c'], max_cluster['r']))

    # graphic output
    if not batch:
        _, main_ax = plt.subplots(2)
        _ = main_ax[0].imshow(pattern)
        _ = main_ax[1].imshow(s)
        plt.show()

    return 0


if __name__ == '__main__':
    sys.exit(main())

