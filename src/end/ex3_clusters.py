#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import matplotlib.pyplot as plt
import library
import mylib

def main():

    file_name, batch = library.get_args()
    header, pixels = mylib.read_image(file_name)
    background, dispersion, _ = mylib.compute_background(pixels)

    # graphic output
    if not batch:
        _, main_ax = plt.subplots()
        main_ax.imshow(pixels)
        plt.show()

    return 0

if __name__ == '__main__':
    sys.exit(main())
