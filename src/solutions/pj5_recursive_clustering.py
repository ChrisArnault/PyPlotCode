#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import numpy as np
import matplotlib.pyplot as plt
import lib_args, lib_wcs, lib_stars, lib_pixels_set
import lib_fits, lib_background, lib_cluster
sys.path.append('../skeletons')


class RecursiveClustering():

    def recursive_call(self, row, column):
        """
         recursively scan pixels starting from one given adress
         accumulate statics of the cluster into the received object
         recursion terminating condition:
           - out of the region boundary
           - already considered pixel
           - pixel below the threshold
           - globally this recursion stops when all connected pixels of this cluster are reached
         we scan pixels up, down, left, right, applying the recursion
        """

        if self.done[row, column] == 1:
            return

        self.done[row, column] = 1

        if self.below[row, column]:
            return

        # accumulate pixel
        self.pixels.add(row, column, self.image[row, column])

        # recurse
        if column < (self.image.shape[1]-1):
            self.recursive_call(row, column + 1)
        if row > 0:
            self.recursive_call(row - 1, column)
        if column > 0:
            self.recursive_call(row, column - 1)
        if row < (self.image.shape[0]-1):
            self.recursive_call(row + 1, column)


    def __call__(self, image, background, dispersion, factor=6.0):

        self.image = image
        self.done = np.zeros_like(image)
        self.below = image < (background+factor*dispersion)

        clusters = []

        for rnum, row in enumerate(image):
            for cnum, _ in enumerate(row):

                self.pixels = lib_pixels_set.PixelsSet()
                self.recursive_call(rnum, cnum)

                # we store only clusters with more than one pixel
                if self.pixels.get_len() > 1:
                    clusters.append(lib_cluster.Cluster(
                        *self.pixels.get_peak(),self.pixels.get_top(),self.pixels.get_integral()))

        # sort by integrals then by top
        max_top = max(clusters, key=lambda cl: cl.top).top
        clusters.sort(key=lambda cl: cl.integral + cl.top / max_top, reverse=True)

        # results
        return clusters


# Main program

def main():

    file_name, interactive = lib_args.get_args()
    header, pixels = lib_fits.read_first_image(file_name)
    background, dispersion, _ = lib_background.compute_background(pixels)

    # search for clusters
    clustering = RecursiveClustering()
    clusters = clustering(pixels, background, dispersion)
    max_cluster = clusters[0]
    wcs = lib_wcs.get_wcs(header)
    pxy = lib_wcs.PixelXY(max_cluster.column, max_cluster.row)
    radec = lib_wcs.xy_to_radec(wcs, pxy)
    cobjects, _, _ = lib_stars.get_celestial_objects(radec)

    # console output
    print('number of clusters: {:2d}, greatest integral: {:7d}, x: {:4.1f}, y: {:4.1f}'.format(
        len(clusters), max_cluster.integral, max_cluster.column, max_cluster.row))
    for cobj in cobjects.keys():
        print('celestial object: {}'.format(cobj))

    # graphic output
    if interactive:
        _, axis = plt.subplots()
        axis.imshow(lib_cluster.add_crosses(pixels, clusters))
        plt.show()

    return 0


if __name__ == '__main__':
    sys.exit(main())

