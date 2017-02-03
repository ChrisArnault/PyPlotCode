#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
import lib_args, lib_fits, lib_background



def main():

    file_name, batch = lib_args.get_args()
    header, pixels = lib_fits.read_first_image(file_name)
    background, dispersion, _ = lib_background.compute_background(pixels)

    # console output
    print('background: {:d}, dispersion: {:d}'.format(int(background),int(dispersion)))

    # graphic output
    if not batch:
        _, axis = plt.subplots()
        axis.imshow(pixels)
        plt.show()

    return 0


if __name__ == '__main__':
    sys.exit(main())
