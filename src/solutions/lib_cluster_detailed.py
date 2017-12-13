#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import math
import numpy as np
sys.path.append('../skeletons')


class Cluster():

    """
    General description of a cluster:
    - its position, with a row and column
    - its integrated value
    """

    def __init__(self, row, column, top, integral ):

        self.row = row
        self.column = column
        self.top = top
        self.integral = integral

    def __str__(self):

        return "{}/{} at {:.1f}, {:.1f}".format(self.top,self.integral,self.row,self.column)


def find_clusters(clusters, row, column, radius):

    """
    From a collection of clusters, return the ones whose distance
    to a given row/column is at most a given radius
    """

    results = []

    for cl in clusters:
        d_row = cl.row-row
        d_col = cl.column-column
        d = math.sqrt(d_row**2+d_col**2)
        if d<=radius:
          results.append(cl)

    return results


class Clustering():

    """
    General clustering algorithm
    """

    def __init__(self, pattern_size=9):
        self.pattern_size = pattern_size

    def _build_pattern(self):
        
        """
        Create a 2D grid of pixels to form a PSF to be applied onto the
        image to detect objects. This pattern has a form of a 2D centered
        normalized gaussian. The size must be odd.
        """

        if self.pattern_size%2 == 0:
            raise ValueError

        x = np.arange(0, self.pattern_size, 1, float)
        y = np.arange(0, self.pattern_size, 1, float)
        # transpose y
        y = y[:, np.newaxis]

        y0 = x0 = self.pattern_size // 2

        # create a 2D gaussian distribution inside this grid.
        sigma = self.pattern_size / 4.0
        pattern = np.exp(-1 * ((x - x0) ** 2 + (y - y0) ** 2) / sigma ** 2)
        pattern = pattern / pattern.sum()

        return pattern

    def _has_peak(self, image, r, c):

        """
        Check if a peak exists at the (r, c) position
        To check if a peak exists:
           - we consider the value at the specified position
           - we verify all values immediately around the specified position are lower
        """

        zone = image[r - 1:r + 2, c - 1:c + 2]
        top = zone[1, 1]
        if top == 0.0 or \
                        zone[0, 0] >= top or \
                        zone[0, 1] >= top or \
                        zone[0, 2] >= top or \
                        zone[1, 0] >= top or \
                        zone[1, 2] >= top or \
                        zone[2, 0] >= top or \
                        zone[2, 1] >= top or \
                        zone[2, 2] >= top:
            return False
        return True

    def _spread_peak(self, image, threshold, r, c):

        """
        Knowing that a peak exists at the specified position, we capture the cluster around it:
        - loop on the distance from center:
          - sum pixels at a given distance
          - increase the distance until the sum falls down below some threshold
        Returns integral, radius, geometric center
        """

        previous_integral = image[r, c]
        radius = 1

        while True:

            integral = np.sum(image[r - radius:r + radius + 1, c - radius:c + radius + 1])
            pixels = 8 * radius
            mean = (integral - previous_integral) / pixels
            if mean < threshold:
                return previous_integral, radius - 1
            elif (r - radius) == 0 or (r + radius + 1) == image.shape[0] or \
                            (c - radius) == 0 or (c + radius + 1) == image.shape[1]:
                return integral, radius
            radius += 1
            previous_integral = integral

    def _convolution_image(self, image):

        """
        principle:
        - at every position of the input image:
            - we apply a fix pattern made of one 2D normalized gaussian distribution
                - width = 9
                - magnitude = 1.0
            - we extract one zone of the original image map with same shape as the pattern
            - this zone is normalized against the greatest magnitude of the image
            - this zone is convoluted with the pattern (convolution product - CP)
            - if the CP is greater than a threshold, the CP is stored at the row/column
                position in a convolution image (CI)
        """

        # we start by building a PSF with a given width
        pattern = self._build_pattern()
        half = self.pattern_size // 2

        # define a convolution image that stores the convolution products at each pixel position
        cp_image = np.zeros((image.shape[0] - 2 * half, image.shape[1] - 2 * half), np.float)

        # loop on all pixels except the border
        for rnum in range(half, image.shape[0] - half):
            for cnum in range(half, image.shape[1] - half):
                rmin = rnum - half
                rmax = rnum + half + 1
                cmin = cnum - half
                cmax = cnum + half + 1

                sub_image = image[rmin:rmax, cmin:cmax]

                # convolution product
                cp_image[rnum - half, cnum - half] = np.sum(sub_image * pattern)

        # result
        return cp_image

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
        ext_image = np.copy(image)
        for n in range(half):
            ext_image = np.insert(ext_image, 0, background, axis=0)
            ext_image = np.insert(ext_image, ext_image.shape[0], background, axis=0)
            ext_image = np.insert(ext_image, 0, background, axis=1)
            ext_image = np.insert(ext_image, ext_image.shape[1], background, axis=1)

        # build the convolution product image
        cp_image = self._convolution_image(ext_image)
        print('conv[4,4]:',int(cp_image[4,4]))
        print('conv[101,4]:',int(cp_image[101,4]))
        print('conv[44,44]:',int(cp_image[44,44]))
        print('conv[61,44]:',int(cp_image[61,44]))
        print('conv[44,61]:',int(cp_image[44,61]))
        print('conv[61,61]:',int(cp_image[61,61]))
        print('conv[4,101]:',int(cp_image[4,101]))
        print('conv[101,101]:',int(cp_image[101,101]))

        # make a copy with a border of 1
        ext_cp_image = np.copy(cp_image)
        ext_cp_image = np.insert(ext_cp_image, 0, background, axis=0)
        ext_cp_image = np.insert(ext_cp_image, ext_cp_image.shape[0], background, axis=0)
        ext_cp_image = np.insert(ext_cp_image, 0, background, axis=1)
        ext_cp_image = np.insert(ext_cp_image, ext_cp_image.shape[1], background, axis=1)
        print('threshold:', int(background + 6.0 * dispersion))

        # scan the convolution image to detect peaks and build clusters
        threshold = background + factor * dispersion
        peaks = []
        for rnum in range(image.shape[0]):
            for cnum in range(image.shape[1]):
                if cp_image[rnum, cnum] <= threshold:
                    continue
                if self._has_peak(ext_cp_image, rnum + 1, cnum + 1):
                    peaks.append((rnum,cnum))
        for npeak, peak in enumerate(peaks):
            print('peak[{}]: {}'.format(npeak,peak))

        # build clusters
        clusters = []
        for n, peak in enumerate(peaks):
            rnum, cnum = peak[0], peak[1]
            integral, radius = self._spread_peak(image, threshold, rnum, cnum)
            print('candidate[{}]: {}, radius: {}'.format(npeak,peak,radius))
            if radius > 0:
                clusters.append(Cluster(rnum, cnum, image[rnum, cnum], integral))

        # sort by integrals then by top
        max_top = max(clusters, key=lambda cl: cl.top).top
        clusters.sort(key=lambda cl: cl.integral + cl.top / max_top, reverse=True)

        # results
        return clusters


    #fig, axis = plt.subplots()
    #_ = axis.imshow(pattern)
    #plt.show()

def add_crosses(image, clusters):
    """
    Return a new image with crosses
    """

    x = 3
    peaks = np.copy(image)
    for cl in clusters:
        rnum, cnum = round(cl.row), round(cl.column)
        peaks[rnum - x:rnum + x + 1, cnum] = image[rnum, cnum]
        peaks[rnum, cnum - x:cnum + x + 1] = image[rnum, cnum]
    return peaks


