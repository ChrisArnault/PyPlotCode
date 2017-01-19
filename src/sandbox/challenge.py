#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Displays a picture of the Bode Galaxy (M81), highlighting the 20 surrounding student regions
Each region is displayed as a square outlined in red labelled after the sudent pair number and shows:
* a black square when the student pair hasn't pushed anything yet
* the highest rank (1, 2, 3 or 4) of successful exercises pushed by the student pair
* the coordinates of the brightest sky object of the region once the student pair has found it

The student regions fits files are expected to be found in a directory named student,
in the same directory as this code file.
They are named NPCnn.fits, where nn is the number of the student pair.

The status of the progression of the student pairs is in a file called spps.txt
The format of each line is
nn<tab>status<tab>celestial object name<tab>celestial object wcs
with nn in range (01,21), status in range (0,5)

:authors Christian Arnault <arnault@lal.in2p3.fr>, Christian Helft <helft@lal.in2p3.fr>
:date   January 2017

"""

import sys

"""
This module provides access to some variables used or maintained by the interpreter
and to functions that interact strongly with the interpreter. It is always available.
"""

sys.path.append('../solutions')
sys.path.append('../skeletons')
"""
add solutions and skeletons directories to system path
"""

import time

"""
Challenge awakens every refresh_rate seconds
"""

import threading

"""
Challenge is implemented as a thread, in order to be able refresh the display
"""

import numpy as np
import matplotlib.pyplot as plt
"""
numerical and display libraries
"""

import lib_fits, lib_wcs
"""
utilities from solutions
"""


datapath = '../../data/fits/'
bode_galaxy_path = datapath + 'M81.fits'
student_regions_directory_path = datapath + "fits"
refresh_rate = 4.0  # in seconds

class Challenge(threading.Thread):

    def __init__(self):

        threading.Thread.__init__(self)

        self.header_M81, self.pixels_M81 = lib_fits.read_first_image(bode_galaxy_path)  # get header and image
        self.wcs_M81 = lib_wcs.get_wcs(self.header_M81)  # get world coordinates of the Bode galaxy

        self.fig, self.main_ax = plt.subplots()  # prepare canvas

        self.y1_max, self.x1_max = self.pixels_M81.shape
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

        for student_pair_number in range(1, 21):
            npacnn_path = datapath + 'NPAC%02d' % student_pair_number + '.fits'
            print(npacnn_path)

            header_nn, pixels_nn = lib_fits.read_first_image(npacnn_path)
            wcs_nn = lib_wcs.get_wcs(header_nn)
            ra0, dec0 = lib_wcs.convert_to_radec(wcs_nn, 0, 0)
            ra1, dec1 = lib_wcs.convert_to_radec(wcs_nn, pixels_nn.shape[0],  pixels_nn.shape[1])

            x0, y0 = lib_wcs.convert_to_xy(self.wcs_M81, ra0, dec0)
            x0, y0 = int(x0), int(y0)
            x1, y1 = x0 + pixels_nn.shape[0], y0 + pixels_nn.shape[1]

            x0 = max(x0, self.border)
            y0 = max(y0, self.border)
            if x1 + self.border > self.x1_max:
                x1 = self.x1_max - self.border
            if y1 + self.border > self.y1_max:
                y1 = self.y1_max - self.border

            print('--------------------------------------------------------')
            print((self.pixels_M81.shape, self.x1_max, self.y1_max))
            print((x0, x1, y0, y1))

            sq = np.zeros_like(pixels_nn)

            border_color = student_pair_number*1500

            self.pixels_M81[y0-self.border:y0, x0-self.border:x1+self.border] = border_color
            self.pixels_M81[y1:y1+self.border, x0-self.border:x1+self.border] = border_color

            self.pixels_M81[y0-self.border:y1+self.border, x0-self.border:x0] = border_color
            self.pixels_M81[y0-self.border:y1+self.border, x1:x1+self.border] = border_color

            self.pixels_M81[y0:y1, x0:x1] = sq[0:y1-y0, 0:x1-x0]

            self.x0[student_pair_number] = x0
            self.x1[student_pair_number] = x1
            self.y0[student_pair_number] = y0
            self.y1[student_pair_number] = y1

            self.draw_text(student_pair_number, '%d:' % (student_pair_number))

        self.imgplot = self.main_ax.imshow(self.pixels_M81)

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

        self.imgplot.set_data(self.pixels_M81)

        self.fig.canvas.draw_idle()

    def run(self):

        while True:

            print('ok')
            plt_lock.acquire()
            self.doit()
            plt_lock.release()
            time.sleep(refresh_rate)




if __name__ == '__main__':

    plt_lock = threading.Lock()
    disp = Challenge()
    disp.start()
    plt.show()

