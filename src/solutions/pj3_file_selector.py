#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-


import sys, os
sys.path.append('../skeletons')
import matplotlib.pyplot as plt
import matplotlib.widgets as widgets
import lib_args, lib_fits


def scan_dir(where):
    filepaths = []
    for dirpath, dirnames, filenames in os.walk(where):
        for filename in filenames:
            if filename.endswith(".fits"):
                filepaths.append(os.path.join(dirpath, filename))
    return filepaths


class UpdateFile():

    def __init__(self, axis, fig):

        self.axis = axis
        self.fig = fig

    def __call__(self, filepath):

        print(filepath)
        header, pixels = lib_fits.read_first_image(filepath)
        imgplot = self.axis.imshow(pixels)
        self.fig.canvas.draw_idle()


def main():

    dirpath, batch = lib_args.get_args()
    filepaths = scan_dir(dirpath)

    # batch console output
    if batch:

        for filepath in filepaths:
            print(filepath)

    # graphic interaction
    else:

        fig, img_axis = plt.subplots(figsize=(10,5))
        plt.subplots_adjust(left=0.05, right=0.45, bottom=0.1, top=0.9)
        buttons_axis = plt.axes([0.55, 0.1, 0.4, 0.8])
        buttons = widgets.RadioButtons(buttons_axis, filepaths)
        callback = UpdateFile(img_axis,fig)
        buttons.on_clicked(callback)
        callback(filepaths[0])
        plt.show()

    return 0


if __name__ == '__main__':
    sys.exit(main())
