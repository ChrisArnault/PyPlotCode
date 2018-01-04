#!/usr/bin/env python
# -*- coding: utf-8 -*-


''' Compute the noise '''


import sys ; sys.path.append('../skeletons')
import numpy as np
from scipy.optimize import curve_fit
import lib_model

def build_pixel_histogram(pixels, sampling_size):
    # Reshape the pixels array as a flat list
    flat = np.asarray(pixels).ravel()

    # build the pixel distribution to extract the background
    y, x = np.histogram(flat, sampling_size)
    return (y, x)

def compute_background(histogram):

    y = histogram[0]
    x = histogram[1]

    # normalize the distribution for the gaussian fit
    my = np.float(np.max(y))
    y = y/my
    mx = np.float(np.max(x))
    x = x[:-1]/mx

    # compute the gaussian fit for the background
    fit, _ = curve_fit(lib_model.gaussian_model, x, y)

    background = fit[1] * mx
    dispersion = abs(fit[2]) * mx
    return background, dispersion, mx, y, x


def tests():

    ''' Unit tests '''

    ## plot the result & the image
    #plt.plot(x, y, 'b+:', label='data')
    #plt.plot(x, gaussian_model(x, maxvalue, background, dispersion), 'r.:', label='fit')
    #plt.legend()
    #plt.title('Flux distribution')
    #plt.xlabel('Amplitude')
    #plt.ylabel('Frequence')
#
    return 0


if __name__ == '__main__':

    sys.exit(tests())


