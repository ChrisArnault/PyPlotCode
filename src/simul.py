#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import matplotlib.pyplot as plt
import numpy as np

import lib_cluster


def build_pattern(size):
    """
    start by creating a 2D grid of pixels to form a PSF to ba applied onto the
    image to detect objects
    this pattern has a form of a 2D centered normalized gaussian
    """

    x = np.arange(0, size, 1, float)
    y = np.arange(0, size, 1, float)
    # transpose y
    y = y[:, np.newaxis]

    y0 = x0 = size / 2

    # create a 2D gaussian distribution inside this grid.
    sigma = size / 5.0
    pattern = 100.0 * np.exp(-1 * ((x - x0) ** 2 + (y - y0) ** 2) / sigma ** 2)

    return pattern


def has_peak(cp_image, r, c):
    """
    Check if a peak exists at the (r0, c0) position of the convolution product matrix cp_image
    To check if a peak exists:
       - we consider the CP et the specified position
       - we verify that ALL CP at positions immediately around the specified position are lower
    """
    zone = cp_image[r - 1:r + 2, c - 1:c + 2]

    # print("has_peak> shape", zone.shape[0], zone.shape[1])

    if (zone.shape[0] < 3) or (zone.shape[1] < 3):
        return False

    top = zone[1, 1]
    if top == 0.0:
        return False, 0.0
    try:
        if zone[0, 0] > top or \
                        zone[0, 1] > top or \
                        zone[0, 2] > top or \
                        zone[1, 0] > top or \
                        zone[1, 2] > top or \
                        zone[2, 0] > top or \
                        zone[2, 1] > top or \
                        zone[2, 2] > top:
            return False
    except:
        print("has_peak> shape error", zone.shape)

    return True


def get_peak(image, cp_image, r, c, threshold, peaks):
    """
    Knowing that a peak exists at the specified position, we capture the cluster around it:
    - loop on the distance from center:
      - sum pixels at a given distance
      - increase the distance until the sum falls down below some threshold
    """

    cp = cp_image[r, c]
    # print('get_peak> peak at [%d %d] %f cp=%f' % (r, c, image[r, c], cp))
    top = image[r, c]
    threshold = top / 7.0
    radius = 1
    while True:
        integral = np.sum(image[r - radius:r + radius + 1, c - radius:c + radius + 1])
        pixels = 8 * radius
        mean = (integral - top) / pixels
        if (mean < threshold) or (r - radius) < 0 or (c - radius) < 0:
            radius -= 1
            # print("get_peak> end ", r - radius, r + radius + 1, c - radius, c + radius + 1, integral, top, radius)
            peaks[r - radius:r + radius + 1, c - radius:c + radius + 1] = image[r - radius:r + radius + 1, c - radius:c + radius + 1]
            break
        # print('   pixels=%d top=%f mean=%f int=%f radius=%d' % (pixels, top, mean, integral, radius))
        top = integral
        radius += 1

    return integral, radius, peaks


def check(pixels):
    import lib_background
    import lib_cluster

    print("-----------------------------------")
    background, dispersion, _ = lib_background.compute_background(pixels)
    print('background: %s, dispersion: %s' % (int(background), int(dispersion)))

    # search for clusters in a sub-region of the image
    threshold = 5.0
    reg = lib_cluster.Region(pixels, background + threshold*dispersion)
    reg.run_convolution()
    max_integral = reg.clusters[0]['integral']

    print('nb clusters: %s, greatest integral: %s' % (len(reg.clusters), max_integral))

    for nc, ic in enumerate(reg.clusters):
        print('cluster', nc, ic['r'], ic['c'], ic['top'], ic['integral'], ic['radius'])
    print("-----------------------------------")



if __name__ == '__main__':
    size = 40
    objects = 3
    max_height = 10000
    threshold = 400.0

    # we create an image size x size
    # then we generate N objects
    # we add some random noise onto it

    image = np.zeros((size, size))
    for o in range(objects):
        sigma = np.random.randint(1, 7)
        height = np.random.randint(5, max_height)

        r = np.random.randint(5, size-5)
        c = np.random.randint(5, size-5)

        print('object at [%d %d] %f (s=%f)' % (r, c, height, sigma))

        cs = np.arange(0, size, 1, float)
        rs = np.arange(0, size, 1, float)
        # transpose y
        rs = rs[:, np.newaxis]

        # create a 2D gaussian distribution inside this grid.
        pattern = height * np.exp(-1 * ((cs - c) ** 2 + (rs - r) ** 2) / sigma ** 2)

        image += pattern

    noise = np.random.rand(size, size) * threshold
    image = image + noise

    check(image)

    # we try the clustering algo
    cp_image = np.zeros_like(image, np.float)

    """
    we start by building a PSF with a given width
    TODO we should study the impact of the size of this pattern
    """
    pattern_width = 9
    pattern = build_pattern(pattern_width)

    half = int(pattern_width / 2)

    # print('half', half)

    cp_threshold = None

    max_region = np.max(image)

    # print(image.shape, pattern.shape)

    for rnum, row in enumerate(image):
        for cnum, col in enumerate(row):

            if image[rnum, cnum] < threshold:
                cp_image[rnum, cnum] = 0
                continue

            """
            rnum, cnum is the center of the convolution zone
            """

            # convolution product
            cmin = cnum - half
            pcmin = 0
            if cmin < 0:
                pcmin = -cmin
                cmin = 0

            cmax = cnum + half
            pcmax = pattern_width - 1
            if cmax > image.shape[1]:
                pcmax = pattern_width - 1 - (cmax - image.shape[1])
                cmax = image.shape[1]

            rmin = rnum - half
            prmin = 0
            if rmin < 0:
                prmin = -rmin
                rmin = 0

            rmax = rnum + half
            prmax = pattern_width - 1
            if rmax > image.shape[0]:
                prmax = pattern_width - 1 - (rmax - image.shape[0])
                rmax = image.shape[0]

            region = image[rmin:rmax, cmin:cmax]

            # print("rnum, cnum, rmin, rmax, cmin, cmax, prmin, prmax, pcmin, pcmax", rnum, cnum, rmin, rmax, cmin, cmax, prmin, prmax, pcmin, pcmax)
            product = np.sum(region * pattern[prmin:prmax, pcmin:pcmax] / max_region)

            if cp_threshold is None or product < cp_threshold:
                # get the lower value of the CP
                cp_threshold = product

            # store the convolution product
            cp_image[rnum, cnum] = product

    cp_threshold *= 4.0

    print('========= end of convolution. Start get peaks', cp_threshold)

    peaks = np.zeros_like(image, np.float)

    for rnum, row in enumerate(cp_image):
        for cnum, col in enumerate(row):

            r0 = rnum
            c0 = cnum

            if cp_image[r0, c0] > cp_threshold:
                """
                r0, c0 is the center of the convolution zone

                check if we have a peak centered at this position:
                - the CP at the center of the zone must be higher then any CP immediately around the center
                """
                peak = has_peak(cp_image, r0, c0)
                if peak and image[r0, c0] > threshold:
                    #
                    # if a peak is detected, we get the cluster
                    #

                    # print('peak at [%d %d] %f' % (r0, c0, image[r0, c0]))
                    x = 3
                    peaks[r0-x:r0+x+1, c0] = image[r0, c0]
                    peaks[r0, c0-x:c0+x+1] = image[r0, c0]

                    integral, radius, peaks = get_peak(image, cp_image, r0, c0, threshold, peaks)
                    print('peak at [%d %d] top=%f radius=%d integral=%f' % (r0, c0, image[r0, c0], radius, integral))

                    # if radius > 3 and integral > 0.0:

    _, main_ax = plt.subplots(2,2)
    _ = main_ax[0, 0].imshow(pattern, interpolation='none')
    _ = main_ax[0, 1].imshow(image, interpolation='none')
    _ = main_ax[1, 0].imshow(cp_image, interpolation='none')
    _ = main_ax[1, 1].imshow(peaks, interpolation='none')

    plt.show()
