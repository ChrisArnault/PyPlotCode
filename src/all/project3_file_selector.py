#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-

import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons
import os


def file_selector(where, select='', callback=None):
    files = []
    n_selected = 0
    width = 0
    for dirname, dirnames, filenames in os.walk(where):
        if dirname == where:
            for i, filename in enumerate(filenames):
                if select != '' and filename.endswith(select):
                    w = ''
                    if where != '':
                        w = where + '/'
                    filename = w + filename
                    files.append(filename)
                    print(filename)
                    if len(filename) > width:
                        width = len(filename)
                    n_selected += 1
        break

    width /= 60.0                # estimated ratio due to font size
    height = 0.04 * n_selected   # estimated ratio due to font size

    axis_fs = plt.axes([0.01, 0.95 - height, width, height])
    fs_widget = RadioButtons(axis_fs, files)
    if callback is not None:
        fs_widget.on_clicked(callback)

    # will attempt to position this widget at the top-left corner
    plt.subplots_adjust(left=width + 0.1, right=0.9)

    # Warning:
    # we have to mark the created object against memory cleanup
    # note that there might be better pattern than using 'return'
    # this method requires to really 'use' the return value in the main global space
    # eg: we may collect this widget into some global database
    return fs_widget


def set_fs(label):
    # dummy action upon file selection
    print(label)


if __name__ == '__main__':
    fig, axis = plt.subplots()
    fs_widget = file_selector('data/student', select='.fits', callback=set_fs)
    plt.show()
