#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
sys.path.append('../skeletons')
import matplotlib.pyplot as plt
import lib_args, lib_fits, lib_background


def main():

    file_name, interactive = lib_args.get_args()
    header, pixels = lib_fits.read_first_image(file_name)
    background, dispersion, _ = lib_background.compute_background(pixels)

    # console output
    print('RESULT: background = {:d}'.format(int(background)))
    print('RESULT: dispersion = {:d}'.format(int(dispersion)))

    # graphic output
    if interactive:
        _, axis = plt.subplots()
        axis.imshow(pixels)
        plt.show()

    return 0


if __name__ == '__main__':
    sys.exit(main())
