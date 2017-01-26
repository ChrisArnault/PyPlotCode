#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Displays a picture of the Bode Galaxy (M81), highlighting (in red) the 20 surrounding student regions.
The picture is refreshed every 4 seconds.
Each region is displayed as a square outlined in red labelled after the sudent pair number and shows:
* a solid square and the highest rank (0-4) of successful exercises pushed by the student pair
* the coordinates of the brightest sky object of the region once the student pair has found it

The student regions (and the Bode galaxy) fits files are expected to be found in a directory named fits,
itself in a same directory data at the root level of the project.
They are named NPCnn.fits, where nn is the number of the student pair.

:authors Christian Arnault <arnault@lal.in2p3.fr>, Christian Helft <helft@lal.in2p3.fr>
:date   January 2017

"""


"""
This module provides access to some variables used or maintained by the interpreter
and to functions that interact strongly with the interpreter. It is always available.
"""
import sys

"""
add solutions and skeletons directories to system path
"""
sys.path.append('../solutions')
sys.path.append('../skeletons')


"""
Challenge awakens every refresh_rate seconds
"""
import time
import datetime

"""
Challenge is implemented as a thread, in order to be able to refresh the display
"""
import threading


"""
numerical and display libraries
"""
import numpy as np
import matplotlib.pyplot as plt

"""
utilities from solutions
"""
import lib_fits, lib_wcs

# Parameters
fits_datapath = '../../data/fits/'
bode_galaxy_path = fits_datapath + 'M81.fits'
student_regions_directory_path = fits_datapath
refresh_rate = 4.0  # in seconds
border_color = 24000  # vibrant red


class Challenge(threading.Thread):

    def __init__(self):

        threading.Thread.__init__(self)

        self.header_M81, self.pixels_M81 = lib_fits.read_first_image(bode_galaxy_path)  # get header and image
        self.wcs_M81 = lib_wcs.get_wcs(self.header_M81)  # and world coordinates of the Bode galaxy

        self.fig, self.main_ax = plt.subplots()  # prepare canvas

        self.y1_max, self.x1_max = self.pixels_M81.shape  # get M81 image dimensions
        self.border = 3  # width of the frame around a student region
        self.font_size = 14
        self.shadow_offset = 1

        # let's build a table of student regions as pairs of (student pair number, region attribute)
        self.x0 = dict()
        self.x1 = dict()
        self.y0 = dict()
        self.y1 = dict()
        self.text = {i:None for i in range(1, 21)}
        self.shadow_text = {i:None for i in range(1, 21)}
        self.student_status = {i:None for i in range(1, 21)}
        self.pixels_nn = {i:None for i in range(1, 21)}

        for student_pair_number in range(1, 21):
            npacnn_path = student_regions_directory_path + 'NPAC%02d' % student_pair_number + '.fits'
            header_nn, pixels_nn = lib_fits.read_first_image(npacnn_path)  # separate header and data
            self.pixels_nn[student_pair_number] = pixels_nn  # and remember data of the student region
            wcs_nn = lib_wcs.get_wcs(header_nn)  # get world coordinates of the student region
            ra0, dec0 = lib_wcs.xy_to_radec(wcs_nn, lib_wcs.PixelXY(0, 0))  # convert to Right Ascension, DEClination

            # get picture coordinates of the student region
            x0, y0 = lib_wcs.radec_to_xy(self.wcs_M81, lib_wcs.RaDec(ra0, dec0))
            x0, y0 = int(x0), int(y0)
            x1, y1 = x0 + pixels_nn.shape[0], y0 + pixels_nn.shape[1]

            # clip out of frame student region
            x0 = max(x0, self.border)
            y0 = max(y0, self.border)
            if x1 + self.border > self.x1_max:
                x1 = self.x1_max - self.border
            if y1 + self.border > self.y1_max:
                y1 = self.y1_max - self.border

           # Fill in the borders of the region
            self.pixels_M81[y0-self.border:y0, x0-self.border:x1+self.border] = border_color
            self.pixels_M81[y1:y1+self.border, x0-self.border:x1+self.border] = border_color
            self.pixels_M81[y0-self.border:y1+self.border, x0-self.border:x0] = border_color
            self.pixels_M81[y0-self.border:y1+self.border, x1:x1+self.border] = border_color

            # Remember region local coordinates
            self.x0[student_pair_number] = x0
            self.x1[student_pair_number] = x1
            self.y0[student_pair_number] = y0
            self.y1[student_pair_number] = y1

        self.imgplot = self.main_ax.imshow(self.pixels_M81)


    def refresh_display(self):
        
        for student_pair_number in range(1, 21):

            # get student pair progression status
            student_pair_progression_status = int((time.time() + student_pair_number) % 6)  # for testing purpose
            celestial_object_found = 'TYC 4383-1121-1'  # for testing purpose

            pixels_nn = self.pixels_nn[student_pair_number] # get back contents of student region
            # get back picture coordinates of the student region
            x0 = self.x0[student_pair_number]
            x1 = self.x1[student_pair_number]
            y0 = self.y0[student_pair_number]
            y1 = self.y1[student_pair_number]

            # Fill in the inside of the region
            if student_pair_progression_status == 5:
                sq = pixels_nn
            else:
                # Get a solid region, from dark to light blue according to the student pair progression
                sq = np.full_like(pixels_nn,2000*student_pair_progression_status)

            self.pixels_M81[y0:y1, x0:x1] = sq[0:y1-y0, 0:x1-x0]  # update the region

            try:
                if student_pair_progression_status != 5:
                    self.draw_text(student_pair_number, '%d:%d' % (student_pair_number, student_pair_progression_status))
                else:
                    self.draw_text(student_pair_number,'%d:' % student_pair_number + celestial_object_found)
            except:
                print(('error in drawing text', student_pair_number, pixels_nn.shape))

    def draw_text(self, i, text):

        x0 = self.x0[i]
        x1 = self.x1[i]
        y0 = self.y0[i]
        y1 = self.y1[i]

        if (self.text[i]) is not None:
            self.shadow_text[i].remove()
        self.shadow_text[i] = plt.text(x0 + self.shadow_offset, int((y0 + y1) / 2) + (self.font_size / 2) + self.shadow_offset, text, fontsize=self.font_size, color='white')
        if (self.text[i]) is not None:
            self.text[i].remove()
        self.text[i]  = plt.text(x0, int((y0+y1)/2)+self.font_size/2, text, fontsize=self.font_size, color='yellow')

    def doit(self):

        self.refresh_display()

        dt = datetime.datetime.now()  # get date and time
        plt.suptitle(dt.strftime("%A, %d. %B %Y %I:%M%p"))

        self.imgplot.set_data(self.pixels_M81)

        self.fig.canvas.draw_idle()


    def run(self):

        while True:  # run forever

            # print ('once more')
            plt_lock.acquire()
            self.doit()
            plt_lock.release()
            time.sleep(refresh_rate)




if __name__ == '__main__':

    plt_lock = threading.Lock()
    disp = Challenge()
    disp.start()
    plt.show()

