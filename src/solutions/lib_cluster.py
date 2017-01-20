#!/usr/bin/env python
# -*- coding: utf-8 -*-


'''
Search clusters in images.
'''


import sys, math
import numpy as np


class Cluster():

    def __init__(self, row, column, integral):

        self.row = row
        self.column = column
        self.integral = integral

    def __str__(self):

        return "{} at {:.1f}, {:.1f}".format(self.integral,self.row,self.column)


def find_clusters(clusters, row, column, radius):

    results = []

    for cl in clusters:
        d_row = cl.row-row
        d_col = cl.column-column
        d = math.sqrt(d_row**2+d_col**2)
        if d<=radius:
          results.append(cl)

    return results


def build_pattern(size):
        
    """
    Start by creating a 2D grid of pixels to form a PSF to be applied onto the
    image to detect objects. This pattern has a form of a 2D centered normalized gaussian.
    The size must be odd.
     """

    if size/2 == 0: raise ValueError

    x = np.arange(0, size, 1, float)
    y = np.arange(0, size, 1, float)
    # transpose y
    y = y[:, np.newaxis]

    y0 = x0 = size // 2

    # create a 2D gaussian distribution inside this grid.
    sigma = size / 4.0
    pattern = np.exp(-1 * ((x - x0) ** 2 + (y - y0) ** 2) / sigma ** 2)

    return pattern


def convolution_clustering(region, threshold):

    def has_peak(cp_image, r, c):

        """
        Check if a peak exists at the (r0, c0) position of the convolution product matrix cp_image
        To check if a peak exists:
           - we consider the CP et the specified position
           - we verify that ALL CP at positions immediately around the specified position are lower
        """

        zone = cp_image[r - 1:r + 2, c - 1:c + 2]
        top = zone[1, 1]
        if top == 0.0:
            return False, 0.0
        if zone[0, 0] > top or \
            zone[0, 1] > top or \
            zone[0, 2] > top or \
            zone[1, 0] > top or \
            zone[1, 2] > top or \
            zone[2, 0] > top or \
            zone[2, 1] > top or \
            zone[2, 2] > top:
            return False
        return True

    def get_peak(region,threshold,cp_image, r, c):

        """
        Knowing that a peak exists at the specified position, we capture the cluster around it:
        - loop on the distance from center:
          - sum pixels at a given distance
          - increase the distance until the sum falls down below some threshold
        """

        cp = cp_image[r, c]
        top = region[r, c]
        radius = 1
        # for radius in range(1, 200):
        while True:
            integral = np.sum(region[r - radius:r + radius + 1, c - radius:c + radius + 1])
            pixels = 8 * radius
            mean = (integral - top) / pixels
            if mean < threshold:
                return integral, radius

            radius += 1
            top = integral

    # define a convolution image that stores the convolution products at each pixel position
    cp_image = np.zeros_like(region, np.float)

    """
    we start by building a PSF with a given width
    TODO we should study the impact of the size of this pattern
    """

    pattern_width = 9
    pattern = build_pattern(pattern_width)

    """
    principle:
    - we scan the complete region (rows/columns)
    - at every position:
        - we apply a fix pattern made of one 2D normalized gaussian distribution
            - width = 9
            - magnitude = 1.0
        - we extract one zone of the original image map with same shape as the pattern
        - this zone is normalized against the greatest magnitude of the image
        - this zone is convoluted with the pattern (convolution product - CP)
        - if the CP is greater than a threshold, the CP is stored at the row/column
            position in a convolution image (CI)
    - we then start a scan of the convolution image (CI):
        - at every position we detect if there is a peak:
            - we extract a 3x3 region of the CI centered at the current position
            - a peak is detected when ALL pixels around the center of this little region are below the center.
        - when a peak is detected, we get the cluster (the group of pixels around a peak):
            - accumulate pixels circularly around the peak until the sum of pixels at a given distance
                is loxer then the threshold
            - we compute the integral of pixel values of the cluster
    - this list of clusters is returned.
    """

    half = int(pattern_width/2)

    cp_threshold = None

    max_region = np.max(region)

    # we keep a guard for pattern in the original image
    for r, row in enumerate(region[half:-half, half:-half]):
        for c, col in enumerate(row):

            rnum = r + half
            cnum = c + half

            if region[rnum, cnum] < threshold:
                cp_image[rnum, cnum] = 0
                continue

            """
            rnum, cnum is the center of the convolution zone
            """

            cmin = cnum - half
            cmax = cnum + half + 1
            rmin = rnum - half
            rmax = rnum + half + 1

            sub_region = region[rmin:rmax, cmin:cmax]

            # convolution product
            product = np.sum(sub_region * pattern / max_region)

            if cp_threshold is None or product < cp_threshold:
                # get the lower value of the CP
                cp_threshold = product

            # store the convolution product
            cp_image[rnum, cnum] = product

    #========= end of convolution. now get peaks

    peaks = np.copy(region)

    # make the CP threshold above the background fluctuations
    cp_threshold *= 1.3

    #
    # scan the convolution image to detect peaks and get all clusters
    #

    clusters = []

    for r, row in enumerate(cp_image[half:-half, half:-half]):
        # print('2) rnum=', rnum)
        for c, col in enumerate(row):

            rnum = r + half
            cnum = c + half

            if cp_image[rnum, cnum] > cp_threshold:
                """
                rnum, cnum is the center of the convolution zone

                check if we have a peak centered at this position:
                - the CP at the center of the zone must be higher then any CP immediately around the center
                """
                peak = has_peak(cp_image, rnum, cnum)
                if peak:
                    #
                    # if a peak is detected, we get the cluster
                    #
                    # print('peak at [%d %d]' % (rnum, cnum))
                    x = 3

                    peaks[rnum - x:rnum + x + 1, cnum] = region[rnum, cnum]
                    peaks[rnum, cnum - x:cnum + x + 1] = region[rnum, cnum]

                    integral, radius = get_peak(region,threshold,cp_image, rnum, cnum)
                    if radius > 1:
                        clusters.append(Cluster(rnum,cnum,integral))

    # sort by  integrals
    clusters.sort(key=lambda cl: cl.integral, reverse=True)

    # results
    return clusters, peaks


# =====
# Unit tests
#=====

if __name__ == '__main__':

    # Cluster
    
    cl = Cluster(2.5,2.5,20)
    print(cl)

    # find_clusters

    cls = [ cl ]
    print("find around 1, 1: ",len(find_clusters(cls,1,1,1)))
    print("find around 2, 2: ",len(find_clusters(cls,2,2,1)))
    
    # build_pattern

    print(build_pattern(3))



