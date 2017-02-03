#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import matplotlib.pyplot as plt
from astropy.io import fits
import lib_args, lib_fits


def main():

    file_name, batch = lib_args.get_args()
    header, pixels = lib_fits.read_first_image(file_name)

    # console output
    print('cd1_1: {CD1_1:.10f}, cd1_2: {CD1_2:.10f}, cd2_1: {CD2_1:.10f}, cd2_2: {CD2_2:.10f}'.format(**header))

    # graphic output
    if not batch:
        _, axis = plt.subplots()
        plt.text(0, -10, file_name, fontsize=14, color='white')
        axis.imshow(pixels)
        plt.show()

    return 0


if __name__ == '__main__':
    sys.exit(main())

