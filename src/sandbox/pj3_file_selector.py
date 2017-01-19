#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-

import sys
sys.path.append('../solutions')

import os
import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons
import lib_args, lib_fits


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

fig = None
main_ax = None

def set_fs(label):
    global fig
    global main_ax

    # dummy action upon file selection
    print(label)

    try:
        header, pixels = lib_fits.read_first_image(label)
    except:
        print('error read_first_image')

    try:
        imgplot = main_ax.imshow(pixels)
        imgplot.set_data(pixels)
        fig.canvas.draw_idle()
    except:
        print('imshow')

if __name__ == '__main__':

    file_name, batch = lib_args.get_args()
    if not batch:

        fig, main_ax = plt.subplots()
        fs_widget = file_selector('../../data/fits', select='.fits', callback=set_fs)
        plt.show()
