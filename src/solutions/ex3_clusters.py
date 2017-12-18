#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
sys.path.append('../skeletons')
sys.path.append('../solutions')
import matplotlib.pyplot as plt
import lib_args, lib_fits, lib_background
import lib_cluster_detailed as lib_cluster


def main():

    file_name, interactive = lib_args.get_args()
    print(file_name)
    header, pixels = lib_fits.read_first_image(file_name)
    background, dispersion, _ = lib_background.compute_background(pixels)

    # search for clusters
    clustering = lib_cluster.Clustering()
    clusters = clustering(pixels, background, dispersion)
    max_cluster = clusters[0]

    # console output
    print('RESULT: clusters_number={:2d}'.format(len(clusters)))
    print('RESULT: cluster_max={:5d}'.format(max_cluster.integral))
    print('RESULT: cluster_max_column={:5d}'.format(max_cluster.column))
    print('RESULT: cluster_max_row={:5d}'.format(max_cluster.row))

    # graphic output
    if interactive:
        _, axes = plt.subplots(2)
        _ = axes[0].imshow(clustering._build_pattern())
        _ = axes[1].imshow(lib_cluster.add_crosses(pixels,clusters))
        plt.show()

    return 0


if __name__ == '__main__':
    sys.exit(main())

