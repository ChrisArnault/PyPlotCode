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

