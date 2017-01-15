#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import matplotlib.pyplot as plt
from astropy.io import fits
import library
import mylib

def main():

    file_name, batch = library.get_args()

    # read image
    with fits.open(file_name) as data_fits:
        data_fits.verify('silentfix')
        header = data_fits[0].header
        pixels = data_fits[0].data
    if header is None:
        return 1

    # console output
    print('cd1_1: {CD1_1:.10f}, cd1_2: {CD1_2:.10f}, cd2_1: {CD2_1:.10f}, cd2_2: {CD2_2:.10f}'.format(**header))

    # graphic output
    if not batch:
        _, main_ax = plt.subplots()
        plt.text(0, -10, file_name, fontsize=14, color='white')
        main_ax.imshow(pixels)
        plt.show()

    return 0

if __name__ == '__main__':
    sys.exit(main())
