#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
sys.path.append('../skeletons')
sys.path.append('../solutions')
import numpy as np
import lib_args, lib_fits, lib_background
import lib_cluster_detailed as lib_cluster


def main():

    file_name, interactive = lib_args.get_args()
    #print(file_name)
    header, pixels = lib_fits.read_first_image(file_name)
    background, dispersion, _ = lib_background.compute_background(pixels)

    # search for clusters
    clustering = lib_cluster.Clustering()
    #   clusters = clustering(pixels, background, dispersion)

    pattern = clustering.step_build_pattern()

    print('RESULT: pattern_sum = {:5.0f}'.format(np.sum(pattern)))

    ext_image = clustering.step_extend_image(pixels)

    print('RESULT: extended_image_width = {:2d}'.format(ext_image.shape[1]))
    print('RESULT: extended_image_height = {:2d}'.format(ext_image.shape[0]))
    print('RESULT: extended_image_sum = {:5.0f}'.format(np.sum(ext_image)))

    cp_image = clustering.step_build_convolution_image(ext_image)

    print('RESULT: convolution_image_width = {:2d}'.format(cp_image.shape[1]))
    print('RESULT: convolution_image_height = {:2d}'.format(cp_image.shape[0]))
    print('RESULT: convolution_image_sum = {:5.0f}'.format(np.sum(cp_image)))

    ext_cp_image = clustering.step_extend_convolution_image(cp_image)

    print('RESULT: extended_convolution_image_width = {:2d}'.format(ext_cp_image.shape[1]))
    print('RESULT: extended_convolution_image_height = {:2d}'.format(ext_cp_image.shape[0]))
    print('RESULT: extended_convolution_image_sum = {:5.0f}'.format(np.sum(ext_cp_image)))

    peaks = clustering.step_detect_peaks(pixels, cp_image, ext_cp_image, background, dispersion)

    print('RESULT: peaks_number = {:2d}'.format(len(peaks)))

    #for npeak, peak in enumerate(peaks):
    #    print('peak[{}]: {}'.format(npeak, peak))
    clusters = clustering.step_build_clusters(pixels, peaks, background, dispersion)

    print('RESULT: clusters_number = {:2d}'.format(len(clusters)))

    clusters, max_top = clustering.step_sort_clusters(clusters)

    print('RESULT: cluster_max_top = {:5d}'.format(max_top))

    max_cluster = clusters[0]

    # console output
    print('RESULT: cluster_max_integral = {:5d}'.format(max_cluster.integral))
    print('RESULT: cluster_max_column = {:5d}'.format(max_cluster.column))
    print('RESULT: cluster_max_row = {:5d}'.format(max_cluster.row))

    # graphic output
    if interactive:
        import matplotlib.pyplot as plt

        _, axes = plt.subplots(2)
        _ = axes[0].imshow(clustering._build_pattern())
        _ = axes[1].imshow(lib_cluster.add_crosses(pixels,clusters))
        plt.show()

    return 0


if __name__ == '__main__':
    sys.exit(main())

