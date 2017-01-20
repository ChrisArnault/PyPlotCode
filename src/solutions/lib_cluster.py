#!/usr/bin/env python
# -*- coding: utf-8 -*-


'''
Search clusters in images.
'''


import sys, math
import numpy as np


class Cluster():

    """
    General description of a cluster:
    - its position, with a row and column
    - its integrated value
    """

    def __init__(self, row, column, integral):

        self.row = row
        self.column = column
        self.integral = integral

    def __str__(self):

        return "{} at {:.1f}, {:.1f}".format(self.integral,self.row,self.column)


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


def _build_pattern(size):
        
    """
    Create a 2D grid of pixels to form a PSF to be applied onto the
    image to detect objects. This pattern has a form of a 2D centered
    normalized gaussian. The size must be odd.
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

def _has_peak(image, r, c):

    """
    Check if a peak exists at the (r, c) position
    To check if a peak exists:
       - we consider the value at the specified position
       - we verify all values immediately around the specified position are lower
    """

    zone = image[r - 1:r + 2, c - 1:c + 2]
    top = zone[1, 1]
    if top == 0.0 or \
        zone[0, 0] > top or \
        zone[0, 1] > top or \
        zone[0, 2] > top or \
        zone[1, 0] > top or \
        zone[1, 2] > top or \
        zone[2, 0] > top or \
        zone[2, 1] > top or \
        zone[2, 2] > top:
        return False
    return True


def _spread_peak(image, threshold, r, c):

    """
    Knowing that a peak exists at the specified position, we capture the cluster around it:
    - loop on the distance from center:
      - sum pixels at a given distance
      - increase the distance until the sum falls down below some threshold
    """

    previous_integral = image[r, c]
    radius = 1
    rmin = r - radius
    rmax = r + radius + 1
    cmin = c - radius
    cmax = c + radius + 1

    while True:

        integral = np.sum(image[rmin:rmax,cmin:cmax])
        pixels = 8 * radius
        mean = (integral - previous_integral) / pixels
        if mean < threshold:
            return integral, radius

        radius += 1
        if rmin>0: rmin = rmin -1
        if rmax<image.shape[0]: rmax = rmax + 1
        if cmin>0: cmin = cmin -1
        if cmax<image.shape[1]: cmax = cmax + 1
        previous_integral = integral


def convolution_clustering(image, threshold):

    # define a convolution image that stores the convolution products at each pixel position
    cp_image = np.zeros_like(image, np.float)

    # we start by building a PSF with a given width
    pattern_width = 9
    pattern = _build_pattern(pattern_width)

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

    half = pattern_width // 2
    cp_threshold = None
    max_image = np.max(image)

    # loop on all pixels except a "half" border
    for rnum in range(half,image.shape[0]-half):
        for cnum in range(half,image.shape[1]-half):

            """
            rnum, cnum is the center of the convolution zone
            """

            if image[rnum, cnum] < threshold:
                cp_image[rnum, cnum] = 0
                continue

            rmin = rnum - half
            rmax = rnum + half + 1
            cmin = cnum - half
            cmax = cnum + half + 1

            sub_image = image[rmin:rmax, cmin:cmax]

            # convolution product
            product = np.sum(sub_image * pattern / max_image)

            if cp_threshold is None or product < cp_threshold:
                # get the lower value of the CP
                cp_threshold = product

            cp_image[rnum, cnum] = product

    # make the CP threshold above the background fluctuations
    cp_threshold *= 1.3

    # scan the convolution image to detect peaks and build clusters
    clusters = []
    for rnum in range(half,image.shape[0]-half):
        for cnum in range(half,image.shape[1]-half):
            if cp_image[rnum, cnum] > cp_threshold:
                peak = _has_peak(cp_image, rnum, cnum)
                if peak:
                    integral, radius = _spread_peak(image, threshold, rnum, cnum)
                    if radius > 1:
                        clusters.append(Cluster(rnum,cnum,integral))

    # sort by  integrals
    clusters.sort(key=lambda cl: cl.integral, reverse=True)

    # results
    return clusters


def add_crosses(image, clusters):

    x = 3
    peaks = np.copy(image)
    for cl in clusters:
        rnum, cnum = cl.row, cl.column
        peaks[rnum - x:rnum + x + 1, cnum] = image[rnum, cnum]
        peaks[rnum, cnum - x:cnum + x + 1] = image[rnum, cnum]
    return peaks


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

    print(_build_pattern(3))

    # has_peak & spread_peak

    image = np.array([
        (0,0,0,0,0),
        (0,1,3,2,0),
        (0,1,3,3,0),
        (0,1,1,1,0),
        (1,0,0,0,0),
    ])
    print(image)

    print(_has_peak(image,2,2))
    print(_has_peak(image,1,3))
    print(_spread_peak(image,1,2,2))

