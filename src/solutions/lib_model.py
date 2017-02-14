#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
sys.path.append('../skeletons')
import numpy as np


def gaussian_model(x, maxvalue, meanvalue, sigma):

    """
    Compute a gaussian function
    """

    return maxvalue * np.exp(-(x - meanvalue)**2 / (2 * sigma**2))


def tests():
    'Unit tests'
    return 0


if __name__ == '__main__':
    sys.exit(tests())


