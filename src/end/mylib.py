#!/usr/bin/env python
# -*- coding: utf-8 -*-

# read image

from astropy.io import fits

def read_image( file_name ):
    with fits.open(file_name) as data_fits:
        data_fits.verify('silentfix')
        header = data_fits[0].header
        pixels = data_fits[0].data
    return header, pixels

# compute background

import numpy as np
from scipy.optimize import curve_fit

def gaussian_model(x, maxvalue, meanvalue, sigma):
    """
    Compute a gaussian function
    """
    return maxvalue * np.exp(-(x - meanvalue)**2 / (2 * sigma**2))

def compute_background(pixels):
    'Compute the noise'

    # Reshape the pixels array as a flat list
    flat = np.asarray(pixels).ravel()

    # sampling size to analyze the background
    sampling_size = 200

    # build the pixel distribution to extract the background
    y, x = np.histogram(flat, sampling_size)

    # normalize the distribution for the gaussian fit
    my = np.float(np.max(y))
    y = y/my
    mx = np.float(np.max(x))
    x = x[:-1]/mx

    # compute the gaussian fit for the background
    fit, _ = curve_fit(gaussian_model, x, y)

    '''
      maxvalue = fit[0] * my
    '''
    background = fit[1] * mx
    dispersion = abs(fit[2]) * mx

    x *= mx
    y *= my

    mx = np.float(np.max(x))

    return background, dispersion, mx

# clustering

class Region(object):

    '''
    Setup a sub-region of the full image
    and initialize the local arrays needed to search all clusters
    '''

    # pylint: disable=too-many-instance-attributes

    def __init__(self, region, threshold):

        '''
        :param region:
        :param threshold:
        :return:
        '''

        global myregion

        myregion = self

        self.threshold = threshold            # above which pixel values are considered
        self.region = region                  # storing the region

        self.done = np.zeros_like(region, float) # a temp array to mark pixels already accessed
        self.below = region < threshold       # a mask of pixels below threshold
        self.shape = region.shape             # save the original region shape
        self.image = region                   # construct the image showing all identified clusters
        self.max = np.max(region)             # initialize the maximum pixel value
        self.clusters = []                    # initialize the cluster list
        self.cluster_dict = dict()            # initialize the cluster dictionary
        self.last_cluster_id = None

        self.trace = np.zeros_like(region)     # a temp array to mark pixels already accessed

    def build_pattern(self, size):
        """
        start by creating a 2D grid of pixels to form a PSF to be applied onto the
        image to detect objects
        this pattern has a form of a 2D centered normalized gaussian
        """

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

        #
        # define a convolution image that stores the convolution products at each pixel position
        #
        cp_image = np.zeros_like(self.region, np.float)

        pattern_width = 9
        pattern = self.build_pattern(pattern_width)

        half = int(pattern_width/2)

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

                # store the convolution product
                cp_image[rnum, cnum] = product

        #========= end of convolution. now get peaks

        peaks = region

        # make the CP threshold above the background fluctuations
        cp_threshold *= 1.3

        # print("cp_threshold", cp_threshold)

        self.cluster_dict = dict()

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
                            self.cluster_dict[integral] = {'r':rnum, 'c':cnum, 'integral':integral, 'top':self.region[rnum, cnum], 'radius':radius, 'cp':cp_image[rnum, cnum]}

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

