#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import numpy as np


def gaussian_model(x, maxvalue, meanvalue, sigma):

    """
    Compute a gaussian function
    """

    return maxvalue * np.exp(-(x - meanvalue)**2 / (2 * sigma**2))


def gaussian_r_model(x, maxvalue, sigma, level):

    """
    ?
    """

    return maxvalue * np.exp(-(x*x) / (2 * (sigma*sigma))) + level


def tests():
    'Unit tests'
    return 0


if __name__ == '__main__':
    sys.exit(tests())


