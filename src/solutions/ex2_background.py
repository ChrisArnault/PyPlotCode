#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
sys.path.append('../skeletons')
import matplotlib.pyplot as plt
import lib_args, lib_fits, lib_background
import numpy as np
import lib_model

def main():

    file_name, interactive = lib_args.get_args()
    header, pixels = lib_fits.read_first_image(file_name)

    z = lib_model.gaussian_model(np.arange(-10.0, 10.0, 1.0), 1.0, 1.0, 1.0)
    print('RESULT: test_gaussian = {:3f}'.format(np.sum(z)))

    y, x = lib_background.build_pixel_histogram(pixels, 200)
    print('RESULT: histogram = {:5d}'.format(np.sum(y)))

    background, dispersion, mx, y, x = lib_background.compute_background((y, x))

    # console output
    print('RESULT: background = {:d}'.format(int(background)))
    print('RESULT: dispersion = {:d}'.format(int(dispersion)))

    # graphic output
    if interactive:
        _, axis = plt.subplots()
        # axis.imshow(pixels)

        z = lib_model.gaussian_model(x, 1.0, background/mx, dispersion/mx)

        plt.plot(x, y, 'b+:', label='data')
        plt.plot(x, z, 'r.:', label='fit')
        plt.legend()
        plt.title('Flux distribution')
        plt.xlabel('Amplitude')
        plt.ylabel('Frequence')

        plt.show()

    return 0


if __name__ == '__main__':
    sys.exit(main())
