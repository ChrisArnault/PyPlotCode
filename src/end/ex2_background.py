#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import matplotlib.pyplot as plt
import library
import mylib

def gaussian_model(x, maxvalue, meanvalue, sigma):
    """
    Compute a gaussian function
    """
    return maxvalue * np.exp(-(x - meanvalue)**2 / (2 * sigma**2))

def main():

    file_name, batch = library.get_args()
    header, pixels = mylib.read_image(file_name)

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

    # console output
    print('background: {:d}, dispersion: {:d}'.format(int(background),int(dispersion)))

    # graphic output
    if not batch:
        _, main_ax = plt.subplots()
        main_ax.imshow(pixels)
        plt.show()

    return 0

if __name__ == '__main__':
    sys.exit(main())
