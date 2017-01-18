#!/usr/bin/env python
# -*- coding: utf-8 -*-


'''
Search clusters in images.
'''


import sys
import numpy as np


class Region():

    '''
    Setup a sub-region of the full image
    and initialize the local arrays needed to search all clusters
    '''

    def __init__(self, region, threshold):

        global myregion

        myregion = self

        self.threshold = threshold            # above which pixel values are considered
        self.region = region                  # storing the region

        self.shape = region.shape             # save the original region shape
        self.image = region                   # construct the image showing all identified clusters
        self.max = np.max(region)             # initialize the maximum pixel value
        self.clusters = []                    # initialize the cluster list
        self.cluster_dict = dict()            # initialize the cluster dictionary
        self.cluster_coords = dict()          # initialize the cluster dictionary keyed with the coordinates
        self.last_cluster_id = None

    def build_pattern(self, size):
        """
        start by creating a 2D grid of pixels to form a PSF to be applied onto the
        image to detect objects
        this pattern has a form of a 2D centered normalized gaussian
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

    def has_peak(self, cp_image, r, c):
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

    def get_peak(self, cp_image, r, c):
        """
        Knowing that a peak exists at the specified position, we capture the cluster around it:
        - loop on the distance from center:
          - sum pixels at a given distance
          - increase the distance until the sum falls down below some threshold
        """

        cp = cp_image[r, c]
        # print('get_peak> peak at [%d %d] %f cp=%f' % (r, c, self.region[r, c], cp))
        top = self.region[r, c]
        radius = 1
        # for radius in range(1, 200):
        while True:
            integral = np.sum(self.region[r - radius:r + radius + 1, c - radius:c + radius + 1])
            pixels = 8 * radius
            mean = (integral - top) / pixels
            if mean < self.threshold:
                # print('   pixels=%d top=%f around=%f int=%f radius=%d' % (pixels, top, mean, integral, radius))
                return integral, radius

            radius += 1
            top = integral


    def run_convolution(self):

        """
        procedure to construct all clusters
        using a convolution based algorithm
        """

        # define a convolution image that stores the convolution products at each pixel position
        cp_image = np.zeros_like(self.region, np.float)

        """
        we start by building a PSF with a given width
        TODO we should study the impact of the size of this pattern
        """
        pattern_width = 9
        pattern = self.build_pattern(pattern_width)
        #print('max2={} shape={} pattern={}'.format(np.max(self.region), repr(self.region.shape), pattern.shape[0]))

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

        #print('half {}'.format(half))

        cp_threshold = None

        region = self.region
        max_region = np.max(region)

        # we keep a guard for pattern in the original image
        for r, row in enumerate(region[half:-half, half:-half]):
            for c, col in enumerate(row):

                rnum = r + half
                cnum = c + half

                if region[rnum, cnum] < self.threshold:
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

                """
                logging.debug('r=%d c=%d [%d:%d, %d:%d] %f',
                              rnum, cnum,
                              rnum, rnum + pattern_width,
                              cnum, cnum + pattern_width,
                              product)
                """

                # store the convolution product
                cp_image[rnum, cnum] = product

        #========= end of convolution. now get peaks

        peaks = np.copy(region)

        # make the CP threshold above the background fluctuations
        cp_threshold *= 1.3

        # print("cp_threshold", cp_threshold)

        self.cluster_dict = dict()
        self.cluster_coords = dict()

        #
        # scan the convolution image to detect peaks and get all clusters
        #
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
                    peak = self.has_peak(cp_image, rnum, cnum)
                    if peak:
                        #
                        # if a peak is detected, we get the cluster
                        #
                        # print('peak at [%d %d]' % (rnum, cnum))
                        x = 3

                        peaks[rnum - x:rnum + x + 1, cnum] = region[rnum, cnum]
                        peaks[rnum, cnum - x:cnum + x + 1] = region[rnum, cnum]

                        integral, radius = self.get_peak(cp_image, rnum, cnum)
                        if radius > 1:
                            # print('peak at [%d %d] %f' % (rnum, cnum, integral, ))
                            cluster = {'r':rnum,
                                       'c':cnum,
                                       'integral':integral,
                                       'top':self.region[rnum, cnum],
                                       'radius':radius,
                                       'cp':cp_image[rnum, cnum]}
                            self.cluster_dict[integral] = cluster
                            coord = "[%f %f]" % (cnum, rnum)
                            # print('coord key=', coord)
                            self.cluster_coords[coord] = cluster

        # ========= end of get peaks. store clusters

        self.clusters = []
        for key in sorted(self.cluster_dict.keys(), reverse=True):
            c = self.cluster_dict[key]
            self.clusters.append(c)

            # print(repr(c))
            rnum = c['r']
            cnum = c['c']
            radius = c['radius']
            cp_image[rnum-radius:rnum+radius+1, cnum-radius:cnum+radius+1] = 12.

        return pattern, cp_image, peaks

    def find_clusters(self, x0, y0, radius):

        results = []

        for x in range(radius*2):
            for y in range(radius*2):
                # coord = '%f %f', x + x0 - radius, y + y0 - radius
                coord = "[%f %f]" % (x + x0 - radius, y + y0 - radius)
                if coord in self.cluster_coords:
                    cluster = self.cluster_coords[coord]
                    results.append(cluster)

        return results


def tests():

    ''' Unit tests '''
    
    return 0


if __name__ == '__main__':
    sys.exit(tests())


