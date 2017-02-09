#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys, time
import concurrent.futures
import numpy as np
import matplotlib.pyplot as plt
import lib_args, lib_fits, lib_background, lib_cluster
sys.path.append('../skeletons')


class SeqFuture:
    def __init__(self, value):
        self.value = value
    def result(self):
        return self.value

class SeqPoolExecutor:
    def submit(self,f,*args,**kwargs):
        return SeqFuture(f(*args,**kwargs))


pool = concurrent.futures.ProcessPoolExecutor()


class ParallelClustering(lib_cluster.Clustering):

    def __init__(self, pattern_size=9):

        lib_cluster.Clustering.__init__(self, pattern_size)

    def _convolution_image(self, pixels):

        # we expect the image to have even sizes
        if pixels.shape[0] % 2 != 0 or pixels.shape[1] % 2 != 0:
            raise ValueError

        # split input image in four parts
        half = self.pattern_size // 2
        rmax = pixels.shape[0]
        cmax = pixels.shape[1]
        nw = pixels[0:(rmax // 2 + half), 0:(cmax // 2 + half)]
        ne = pixels[0:(rmax // 2 + half), (cmax // 2 - half):cmax]
        sw = pixels[(rmax // 2 - half):rmax, 0:(cmax // 2 + half)]
        se = pixels[(rmax // 2 - half):rmax, (cmax // 2 - half):cmax]

        # compute convolution product images
        future_cp_nw = pool.submit(lib_cluster.Clustering._convolution_image, self, nw)
        future_cp_ne = pool.submit(lib_cluster.Clustering._convolution_image, self, ne)
        future_cp_sw = pool.submit(lib_cluster.Clustering._convolution_image, self, sw)
        future_cp_se = pool.submit(lib_cluster.Clustering._convolution_image, self, se)

        # join convolution product images
        cp_pixels = np.zeros((pixels.shape[0] - 2 * half, pixels.shape[1] - 2 * half), np.float)
        cp_pixels[0:rmax // 2 - half, 0:cmax // 2 - half] = future_cp_nw.result()
        cp_pixels[0:rmax // 2 - half, cmax // 2 - half:cmax - 2 * half] = future_cp_ne.result()
        cp_pixels[rmax // 2 - half:rmax - 2 * half, 0:cmax // 2 - half] = future_cp_sw.result()
        cp_pixels[rmax // 2 - half:rmax - 2 * half, cmax // 2 - half:cmax - 2 * half] = future_cp_se.result()

        return cp_pixels

    def __call__(self, image, background, dispersion, factor=6.0):

        """
        principle:
        - we then start a scan of the convolution image (CI):
            - at every position we detect if there is a peak:
                - we extract a 3x3 region of the CI centered at the current position
                - a peak is detected when ALL pixels around the center of this little region are below the center.
            - when a peak is detected, we get the cluster (the group of pixels around a peak):
                - accumulate pixels circularly around the peak until the sum of pixels at a given distance
                    is lower than the threshold
                - we compute the integral of pixel values of the cluster
        - this list of clusters is returned.
        """

        # make a copy with a border of half
        half = self.pattern_size // 2

        def extend_image(img, border, value):
            extended = np.zeros(np.array(img.shape) + border * 2) + value
            extended[border:-border, border:-border] = img
            return extended

        ext_image = extend_image(image, half, background)

        # build the convolution product image
        # receive an image with a "half" border, and
        # return an image without border
        cp_image = self._convolution_image(ext_image)

        # make a copy with a border of 1
        ext_cp_image = extend_image(cp_image, 1, background)

        # scan the convolution image to detect peaks
        threshold = background + factor * dispersion
        peaks = []
        for rnum, row in enumerate(cp_image):
            for cnum, pixel in enumerate(row):
                if pixel <= threshold:
                    continue
                if not self._has_peak(ext_cp_image, rnum + 1, cnum + 1):
                    continue
                peaks.append((rnum, cnum))

        # build the future candidate clusters from the detected peaks
        candidates = []
        for rnum, cnum in peaks:
            future_integral_radius = pool.submit(lib_cluster.Clustering._spread_peak,self, image, threshold, rnum, cnum)
            candidates.append((rnum, cnum, future_integral_radius))

        # scan the candidates and build clusters
        clusters = []
        for rnum, cnum, future_integral_radius in candidates:
            integral, radius = future_integral_radius.result()
            if radius > 0:
                clusters.append(lib_cluster.Cluster(rnum, cnum, image[rnum, cnum], integral))

        # sort by integrals
        max_top = max(clusters, key=lambda cl: cl.top).top
        clusters.sort(key=lambda cl: cl.integral + cl.top / max_top, reverse=True)

        # results
        return clusters


# Main program

def main():

    file_name, batch = lib_args.get_args()
    header, pixels = lib_fits.read_first_image(file_name)
    background, dispersion, _ = lib_background.compute_background(pixels)

    # search for clusters
    time0 = time.time()
    clustering = ParallelClustering()
    clusters = clustering(pixels, background, dispersion)
    time1 = time.time()
    max_cluster = clusters[0]

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
