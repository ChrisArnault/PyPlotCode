#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import matplotlib.pyplot as plt
import matplotlib.widgets as widgets
import lib_args, lib_fits, lib_background


class UpdateSlider():

    def __init__(self, pixels, imgplot, fig):

        self.pixels = pixels
        self.imgplot = imgplot
        self.fig = fig

    def __call__(self, val):

        above = self.pixels >= val
        new_pixels = self.pixels * above - above * val
        self.imgplot.set_data(new_pixels)
        self.fig.canvas.draw_idle()


def main():

    file_name, batch = lib_args.get_args()
    header, pixels = lib_fits.read_first_image(file_name)
    background, dispersion, max_x = lib_background.compute_background(pixels)

    # console output
    print('background: {:d}, dispersion: {:d}'.format(int(background),int(dispersion)))

    # graphic output
    if not batch:

        fig, axis = plt.subplots()
        imgplot = axis.imshow(pixels)

        ax_thresh = plt.axes([0.25, 0.92, 0.65, 0.03])
        s_thresh = widgets.Slider(ax_thresh, 'Threshold', 0.0, max_x, valinit=background)

        update_slider = UpdateSlider(pixels,imgplot,fig)
        s_thresh.on_changed(update_slider)
        update_slider(background)

        plt.show()

    return 0


if __name__ == '__main__':
    sys.exit(main())
