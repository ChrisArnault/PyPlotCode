#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
sys.path.append('../skeletons')
import matplotlib.pyplot as plt
import lib_args, lib_fits, lib_background, lib_cluster


def main():

    file_name, batch = lib_args.get_args()
    header, pixels = lib_fits.read_first_image(file_name)
    background, dispersion, _ = lib_background.compute_background(pixels)

    # search for clusters
    clustering = lib_cluster.Clustering()
    clusters = clustering.convolution_clustering(pixels, background, dispersion)
    max_cluster = clusters[0]

    # console output
    print('number of clusters: {:2d}, greatest integral: {:7d}, x: {:4.1f}, y: {:4.1f}'.format(
        len(clusters), max_cluster.integral, max_cluster.column, max_cluster.row))

    # graphic output
    if not batch:
        _, axes = plt.subplots(2)
        _ = axes[0].imshow(lib_cluster._build_pattern(9))
        _ = axes[1].imshow(lib_cluster.add_crosses(pixels,clusters))
        plt.show()

    return 0


if __name__ == '__main__':
    sys.exit(main())

