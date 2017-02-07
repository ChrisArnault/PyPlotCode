#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys, time
sys.path.append('../skeletons')
import numpy as np
import matplotlib.pyplot as plt
import lib_args, lib_fits, lib_background, lib_cluster


# Substitute a parallel convolution_image() within lib_cluster

sequential_convolution_image = lib_cluster._convolution_image

def parallel_convolution_image(pixels):

    # split input image
    half = lib_cluster.PATTERN_SIZE // 2
    rmax = pixels.shape[0]
    cmax = pixels.shape[1]
    nw = pixels[0:(rmax//2+half),0:(cmax//2+half)]
    ne = pixels[0:(rmax//2+half),(cmax//2-half):cmax]
    sw = pixels[(rmax//2-half):rmax,0:(cmax//2+half)]
    se = pixels[(rmax//2-half):rmax,(cmax//2-half):cmax]

    # compute convolution product images
    cp_nw = sequential_convolution_image(nw)
    cp_ne = sequential_convolution_image(ne)
    cp_sw = sequential_convolution_image(sw)
    cp_se = sequential_convolution_image(se)

    # join convolution product images
    cp_pixels = np.zeros((pixels.shape[0]-2*half,pixels.shape[1]-2*half), np.float)
    cp_pixels[0:rmax//2-half,0:cmax//2-half] = cp_nw
    cp_pixels[0:rmax//2-half,cmax//2-half:cmax-2*half] = cp_ne
    cp_pixels[rmax//2-half:rmax-2*half,0:cmax//2-half] = cp_sw
    cp_pixels[rmax//2-half:rmax-2*half,cmax//2-half:cmax-2*half] = cp_se

    return cp_pixels

lib_cluster._convolution_image = parallel_convolution_image


# Main program

def main():

    file_name, batch = lib_args.get_args()
    header, pixels = lib_fits.read_first_image(file_name)
    background, dispersion, _ = lib_background.compute_background(pixels)

    # search for clusters
    time0 = time.time()
    clusters = lib_cluster.convolution_clustering(pixels, background, dispersion)
    time1 = time.time()
    max_cluster = clusters[0]

    # console output
    print('number of clusters: {:2d}, greatest integral: {:7d}, x: {:4.1f}, y: {:4.1f}'.format(
        len(clusters), max_cluster.integral, max_cluster.column, max_cluster.row))
    print('clustering execution time: {:.3f} seconds'.format(time1-time0))

    # graphic output
    if not batch:
        _, axis = plt.subplots()
        axis.imshow(lib_cluster.add_crosses(pixels,clusters))
        plt.show()

    return 0


if __name__ == '__main__':
    sys.exit(main())

