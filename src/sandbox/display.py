#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys, argparse, time, threading
import numpy as np
import matplotlib.pyplot as plt
from lib_logging import logging
import lib_fits, lib_wcs

DATAPATH = 'data/'
DATAFILE = 'M81'


class Display(threading.Thread):

    def __init__(self):

        threading.Thread.__init__(self)

        self.m81 = DATAPATH + 'misc/M81' + '.fits'
        self.header_m81, self.pixels_m81 = lib_fits.read_first_image(self.m81)
        self.wcs_m81 = lib_wcs.get_wcs(self.header_m81)

        self.fig, self.main_ax = plt.subplots()

        self.y1_max, self.x1_max = self.pixels_m81.shape
        self.border = 10
        self.font_size = 14
        self.shadow = 3

        self.x0 = dict()
        self.x1 = dict()
        self.y0 = dict()
        self.y1 = dict()
        self.text = dict()
        self.text2 = dict()

        self.counter = 0

        for i in range(1, 21):
            npacnn = DATAPATH + 'student/NPAC%02d' % i + '.fits'
            print(npacnn)

            header_nn, pixels_nn = lib_fits.read_first_image(npacnn)

            x0, y0 = 0 , 0
            x1, y1 = x0 + pixels_nn.shape[0], y0 + pixels_nn.shape[1]

            if x0 - self.border < 0:
                x0 = self.border
            if y0 - self.border < 0:
                y0 = self.border

            if x1 + self.border > self.x1_max:
                x1 = self.x1_max - self.border
            if y1 + self.border > self.y1_max:
                y1 = self.y1_max - self.border

            print('--------------------------------------------------------')
            print((self.pixels_m81.shape, self.x1_max, self.y1_max))
            print((x0, x1, y0, y1))

            sq = np.zeros_like(pixels_nn)

            border_color = i*1500

            self.pixels_m81[y0-self.border:y0, x0-self.border:x1+self.border] = border_color
            self.pixels_m81[y1:y1+self.border, x0-self.border:x1+self.border] = border_color

            self.pixels_m81[y0-self.border:y1+self.border, x0-self.border:x0] = border_color
            self.pixels_m81[y0-self.border:y1+self.border, x1:x1+self.border] = border_color

            self.pixels_m81[y0:y1, x0:x1] = sq[0:y1-y0, 0:x1-x0]

            self.x0[i] = x0
            self.x1[i] = x1
            self.y0[i] = y0
            self.y1[i] = y1

            self.draw_text(i, '%d:' % (i))

        self.imgplot = self.main_ax.imshow(self.pixels_m81)

    def draw_text(self, i, text):

        x0 = self.x0[i]
        x1 = self.x1[i]
        y0 = self.y0[i]
        y1 = self.y1[i]

        self.text[i]  = plt.text(x0, int((y0+y1)/2)+self.font_size/2, text, fontsize=self.font_size, color='red')
        self.text2[i] = plt.text(x0+self.shadow, int((y0+y1)/2) + (self.font_size/2) + self.shadow, text, fontsize=self.font_size, color='white')

    def doit(self):

        self.counter += 1

        for i in range(1, 21):
            x0 = self.x0[i]
            x1 = self.x1[i]
            y0 = self.y0[i]
            y1 = self.y1[i]

            if (self.text[i]) is not None:
                self.text[i].remove()
                self.text[i] = None
                self.text2[i].remove()
                self.text2[i] = None

            try:
                self.draw_text(i, '%d:%d' % (i, self.counter))
            except:
                print(('===========>', i, pixels_nn.shape))


            print('--------------------------------------------------------')

        self.imgplot.set_data(self.pixels_m81)

        self.fig.canvas.draw_idle()

    def run(self):

        while True:

            print('ok')
            plt_lock.acquire()
            self.doit()
            plt_lock.release()
            time.sleep(4.0)




if __name__ == '__main__':

    plt_lock = threading.Lock()
    disp = Display()
    disp.start()
    plt.show()
