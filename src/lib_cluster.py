#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Search clusters in images.
'''

import sys
import numpy as np
from lib_logging import logging
import threading
import time
import random

import matplotlib.pyplot as plt

total_pixels = 0
sleep_in_cluster = 0.4
sleep_in_scanning = 0.001

strategies = ('random', 'all', 'center', '4centers')
mystrategy = 'random'

mycolormap = 'seismic'
'''
# mycolormap = 'Blues'
# mycolormap = 'bone'
# mycolormap = 'hot'
'''

myregion = None

plt_id = 0

class PLT():
    def __init__(self):
        global plt_id

        self.image = None
        self.figure = None
        self.imgplot = None
        self.main_axis = None
        self.image = np.zeros([100, 100])
        self.figure, self.main_axis = plt.subplots()
        self.imgplot = self.main_axis.imshow(self.image, interpolation='none', cmap=mycolormap, animated=True)
        self.figure.colorbar(self.imgplot)
        self.id = plt_id
        plt_id += 1

    def start(self):
        global myregion

        print('starting plt %d' % self.id)
        myregion.run_threaded()

        plt.show()

    def fill_border(self):

        border_color = 0x8000
        border = 1

        w = self.image.shape[0]
        h = self.image.shape[1]

        self.image[0:, 0:border] = border_color
        self.image[0:, -border:] = border_color

        self.image[0:border, 0:] = border_color
        self.image[-border:, 0:] = border_color


    def change_image(self, image):
        self.image = np.zeros_like(image)
        # self.fill_border()
        self.imgplot = self.main_axis.imshow(self.image, interpolation='none', cmap=mycolormap, animated=True)
        self.figure.canvas.draw_idle()

    def redraw(self, column, row, color):
        self.image[column, row] = color

        try:
            self.imgplot = self.main_axis.imshow(self.image, interpolation='none', cmap=mycolormap)
            self.figure.canvas.draw_idle()
        except:
            print('error')

drawer = None

class TCluster(object):

    '''
    A cluster is a...
    '''

    # pylint: disable=too-many-instance-attributes

    def __init__(self, cluster_id, trace=None):
        '''
        :param cluster_id:
        :return:
        '''
        self.id = cluster_id
        self.integral = 0
        self.pixels = []
        self.centroid = None
        self.min_row = None
        self.max_row = None
        self.min_column = None
        self.max_column = None
        self.neighbours = dict()

        self.trace = trace


    def min(self, attr, value):
        '''
        :param attr:
        :param value:
        :return:
        '''
        if hasattr(self, attr):
            if (getattr(self, attr) is None) or (value < getattr(self, attr)):
                setattr(self, attr, value)
        else:
            setattr(self, attr, value)

    def max(self, attr, value):
        '''
        :param attr:
        :param value:
        :return:
        '''
        if hasattr(self, attr):
            if (getattr(self, attr) is None) or (value > getattr(self, attr)):
                setattr(self, attr, value)
        else:
            setattr(self, attr, value)

    def min_max(self, attr, value):
        '''
        :param attr:
        :param value:
        :return:
        '''
        self.min('min_' + attr, value)
        self.max('max_' + attr, value)

    def add(self, row, column, value):
        '''
        :param row:
        :param column:
        :param value:
        :return:
        '''
        global total_pixels
        global drawer

        # Do not penalize non-threaded version
        if drawer is not None and threading.active_count() > 1:
            total_pixels += 1

            drawer.redraw(column, row, 1500 * self.id)

            time.sleep(sleep_in_cluster)

        self.pixels.append((row, column, value))

        # FIXME: THIS COMPUTING OF THE CENTROID IS NOT USED ANY MORE IN
        # THE NEW IMPLEMENTATION

        self.min_max('row', row)
        self.min_max('column', column)

        centroid_row = (self.min_row+self.max_row)/2.0
        centroid_column = (self.min_column+self.max_column)/2.0
        self.centroid = (centroid_row, centroid_column)

        # FIXME: Weighted centroid implementation. Remove previous lines and uncomment
        # to activate.
        #if self.centroid is not None:
        #    if value > self.centroid[2]:
        #        # print 'centroid %d row=%d col=%d' % (self.id, row, column)
        #        self.centroid = (row, column, value)
        #else:
        #    # print 'centroid %d row=%d col=%d' % (self.id, row, column)
        #    self.centroid = (row, column, value)

        self.integral += value


    # FIXME: THIS COMPUTING OF THE CENTROID IS NOT USED ANY MORE IN
    # THE NEW IMPLEMENTATION

    def get_centroid(self):

        pixels = len(self.pixels)
        if pixels == 0:
            return None, None

        row_mean = sum([pixel[0] for pixel in self.pixels]) / pixels
        col_mean = sum([pixel[1] for pixel in self.pixels]) / pixels

        row_weight = sum([pixel[2]*((pixel[0] - row_mean)**2) for pixel in self.pixels])
        col_weight = sum([pixel[2]*((pixel[1] - row_mean)**2) for pixel in self.pixels])
        row_weight = np.sqrt(row_weight)/self.integral + row_mean
        col_weight = np.sqrt(col_weight)/self.integral + col_mean

        return row_weight, col_weight

class LockContext(object):
    def __init__(self, lock):
        self.lock = threading.Lock()
    def __enter__(self):
        self.lock.acquire()
        return self.lock
    def __exit__(self, type, value, traceback):
        self.lock.release()

class TClusterFactory(threading.Thread):
    def __init__(self, region, row, column, cluster_id, trace=None):
        threading.Thread.__init__(self)

        self.threadID = cluster_id
        self.name = 'c%d' % cluster_id

        self.region = region
        self.shape = region.shape
        self.row = row
        self.column = column
        self.cluster = TCluster(cluster_id, trace)
        # with LockContext(self.region.region_lock):
        self.region.clusters.append(self.cluster)
        self.cluster_id = cluster_id

    def scan_neighbours(self, row, column):
        """
         recursively scan pixels starting from one given adress
         accumulate statics of the cluster into the received object
         recursion terminating condition:
           - out of the region boundary
           - already considered pixel
           - pixel below the threshold
           - globally this recursion stops when all connected pixels of this cluster are reached
         we scan pixels up, down, left, right, applying the recursion
        """

        # are we still within the shape?
        if row < 0:
            return 'out'
        if row >= self.shape[0]:
            return 'out'
        if column < 0:
            return 'out'
        if column >= self.shape[1]:
            return 'out'

        # get ownership for this pixel if not used yet
        # with LockContext(self.region.region_lock):
        if True:
            if self.region.done[row, column] == self.cluster_id:
                return 'done'
            if self.region.done[row, column] > 0:
                return '%s' % self.region.done[row, column]

            self.region.done[row, column] = self.cluster_id

            # now this pixel is ours => we may use it
            if self.region.below[row, column]:
                return 'below'

            # add this pixel to the filtered image
            # with LockContext(self.region.image_lock):
            self.region.image[row, column] = self.region.region[row, column]

            # accumulate statistics
            self.cluster.add(row, column, self.region.region[row, column])

        # recurse
        if column < self.shape[1]:
            status = self.scan_neighbours(row, column+1)
            if status not in ('done', 'below', 'out'):
                self.cluster.neighbours[status] = True
        if row > 0:
            status = self.scan_neighbours(row-1, column)
            if status not in ('done', 'below', 'out'):
                self.cluster.neighbours[status] = True
        if column > 0:
            status = self.scan_neighbours(row, column-1)
            if status not in ('done', 'below', 'out'):
                self.cluster.neighbours[status] = True
        if row < self.shape[0]:
            status = self.scan_neighbours(row+1, column)
            if status not in ('done', 'below', 'out'):
                self.cluster.neighbours[status] = True

        return 'done'

    def run(self):
        self.scan_neighbours(self.row, self.column)


class RegionRunner(threading.Thread):
    def __init__(self, region, strategy):
        threading.Thread.__init__(self)
        self.region = region
        self.strategy = strategy

    def run(self):
        width = self.region.shape[0]
        height = self.region.shape[1]

        cluster_id = 0

        if self.strategy == 'random':
            n = width * height
            arr = np.arange(n)
            np.random.shuffle(arr)
            arr = arr.reshape((width, height))
            for rnum, row in enumerate(arr):
                for cnum, val in enumerate(row):
                    cnum = int(val/height)
                    rnum = val % width
                    self.region.one_pixel(int(cnum), int(rnum), cluster_id)
                    cluster_id += 1
                    time.sleep(sleep_in_scanning)
        if self.strategy == 'all':
            for rnum, row in enumerate(self.region.region):
                for cnum, _ in enumerate(row):
                    self.region.one_pixel(cnum, rnum, cluster_id)
                    cluster_id += 1
                    time.sleep(sleep_in_scanning)
        if self.strategy == 'center':
            rnum = int(width/2)
            cnum = int(height/2)
            self.region.one_pixel(cnum, rnum, cluster_id)
        if self.strategy == '4centers':
            rcenter = int(width/2)
            ccenter = int(height/2)
            side = 2
            cluster_id = 0
            for rnum in [-side, side]:
                rnum = rcenter + rnum
                for cnum in [-side, side]:
                    cnum = ccenter + cnum
                    self.region.one_pixel(cnum, rnum, cluster_id)
                    cluster_id += 1

class Region(object):

    '''
    Setup a sub-region of the full image
    and initialize the local arrays needed to search all clusters
    '''

    # pylint: disable=too-many-instance-attributes

    def __init__(self, region, threshold):

        '''
        :param region:
        :param threshold:
        :return:
        '''

        global myregion


        myregion = self

        logging.debug('Region> threshold {}'.format(threshold))

        self.threshold = threshold            # above which pixel values are considered
        self.region = region                  # storing the region

        self.done = np.zeros_like(region, float) # a temp array to mark pixels already accessed
        self.below = region < threshold       # a mask of pixels below threshold
        self.shape = region.shape             # save the original region shape
        self.image = region                   # construct the image showing all identified clusters
        self.max = np.max(region)             # initialize the maximum pixel value
        self.clusters = []                    # initialize the cluster list
        self.cluster_dict = dict()            # initialize the cluster dictionary
        self.last_cluster_id = None

        self.trace = np.zeros_like(region)     # a temp array to mark pixels already accessed

    def animate(self, in_cluster=None, in_scanning=None, strategy=None):
        global drawer
        global sleep_in_cluster
        global sleep_in_scanning
        global mystrategy

        if in_cluster is not None:
            sleep_in_cluster = in_cluster

        if in_scanning is not None:
            sleep_in_scanning = in_scanning

        if strategy is not None and strategy in strategies:
            mystrategy = strategy

        print('start animate region')

        drawer = PLT()
        drawer.fill_border()
        drawer.start()

    def recursive_build_cluster(self, row, column, obj):
        """
         recursively scan pixels starting from one given adress
         accumulate statics of the cluster into the received object
         recursion terminating condition:
           - out of the region boundary
           - already considered pixel
           - pixel below the threshold
           - globally this recursion stops when all connected pixels of this cluster are reached
         we scan pixels up, down, left, right, applying the recursion
        """
        if row < 0:
            return
        if row >= self.shape[0]:
            return
        if column < 0:
            return
        if column >= self.shape[1]:
            return

        if self.done[row, column] == 1:
            return

        self.done[row, column] = 1

        if self.below[row, column]:
            return

        # add this pixel to the filtered image
        self.image[row, column] = self.region[row, column]

        # accumulate statistics
        obj.add(row, column, self.region[row, column])

        # recurse
        if column < self.shape[1]:
            self.recursive_build_cluster(row, column + 1, obj=obj)
        if row > 0:
            self.recursive_build_cluster(row - 1, column, obj=obj)
        if column > 0:
            self.recursive_build_cluster(row, column - 1, obj=obj)
        if row < self.shape[0]:
            self.recursive_build_cluster(row + 1, column, obj=obj)

    def build_pattern(self, size):
        """
        start by creating a 2D grid of pixels to form a PSF to be applied onto the
        image to detect objects
        this pattern has a form of a 2D centered normalized gaussian
        """
        if size/2 == 0:
          logging.critical('Even pattern size')

        x = np.arange(0, size, 1, float)
        y = np.arange(0, size, 1, float)
        # transpose y
        y = y[:, np.newaxis]

        y0 = x0 = size // 2

        # create a 2D gaussian distribution inside this grid.
        sigma = size / 4.0
        pattern = np.exp(-1 * ((x - x0) ** 2 + (y - y0) ** 2) / sigma ** 2)

        return pattern

    def has_peak(self, cp_image, r, c):
        """
        Check if a peak exists at the (r0, c0) position of the convolution product matrix cp_image
        To check if a peak exists:
           - we consider the CP et the specified position
           - we verify that ALL CP at positions immediately around the specified position are lower
        """
        zone = cp_image[r - 1:r + 2, c - 1:c + 2]
        top = zone[1, 1]
        if top == 0.0:
            return False, 0.0
        if zone[0, 0] > top or \
                        zone[0, 1] > top or \
                        zone[0, 2] > top or \
                        zone[1, 0] > top or \
                        zone[1, 2] > top or \
                        zone[2, 0] > top or \
                        zone[2, 1] > top or \
                        zone[2, 2] > top:
            return False
        return True

    def get_peak(self, cp_image, r, c):
        """
        Knowing that a peak exists at the specified position, we capture the cluster around it:
        - loop on the distance from center:
          - sum pixels at a given distance
          - increase the distance until the sum falls down below some threshold
        """

        cp = cp_image[r, c]
        # print('get_peak> peak at [%d %d] %f cp=%f' % (r, c, self.region[r, c], cp))
        top = self.region[r, c]
        radius = 1
        # for radius in range(1, 200):
        while True:
            integral = np.sum(self.region[r - radius:r + radius + 1, c - radius:c + radius + 1])
            pixels = 8 * radius
            mean = (integral - top) / pixels
            if mean < self.threshold:
                # print('   pixels=%d top=%f around=%f int=%f radius=%d' % (pixels, top, mean, integral, radius))
                return integral, radius

            radius += 1
            top = integral


    def run_convolution(self):
        """
        procedure to construct all clusters
        using a convolution based algorithm
        """

        #
        # define a convolution image that stores the convolution products at each pixel position
        #
        cp_image = np.zeros_like(self.region, np.float)

        """
        we start by building a PSF with a given width
        TODO we should study the impact of the size of this pattern
        """
        pattern_width = 9
        pattern = self.build_pattern(pattern_width)
        logging.debug('max2=%d shape=%s pattern=%d', np.max(self.region), repr(self.region.shape), pattern.shape[0])

        """
        principle:
        - we scan the complete region (rows/columns)
        - at every position:
            - we apply a fix pattern made of one 2D normalized gaussian distribution
                - width = 9
                - magnitude = 1.0
            - we extract one zone of the original image map with same shape as the pattern
            - this zone is normalized against the greatest magnitude of the image
            - this zone is convoluted with the pattern (convolution product - CP)
            - if the CP is greater than a threshold, the CP is stored at the row/column
                position in a convolution image (CI)
        - we then start a scan of the convolution image (CI):
            - at every position we detect if there is a peak:
                - we extract a 3x3 region of the CI centered at the current position
                - a peak is detected when ALL pixels around the center of this little region are below the center.
            - when a peak is detected, we get the cluster (the group of pixels around a peak):
                - accumulate pixels circularly around the peak until the sum of pixels at a given distance
                    is loxer then the threshold
                - we compute the integral of pixel values of the cluster
        - this list of clusters is returned.
        """

        half = int(pattern_width/2)

        logging.debug('half %d', half)

        cp_threshold = None

        region = self.region
        max_region = np.max(region)

        # we keep a guard for pattern in the original image
        for r, row in enumerate(region[half:-half, half:-half]):
            for c, col in enumerate(row):

                rnum = r + half
                cnum = c + half

                if region[rnum, cnum] < self.threshold:
                    cp_image[rnum, cnum] = 0
                    continue

                """
                rnum, cnum is the center of the convolution zone
                """

                cmin = cnum - half
                cmax = cnum + half + 1
                rmin = rnum - half
                rmax = rnum + half + 1

                sub_region = region[rmin:rmax, cmin:cmax]

                # convolution product
                product = np.sum(sub_region * pattern / max_region)

                if cp_threshold is None or product < cp_threshold:
                    # get the lower value of the CP
                    cp_threshold = product

                """
                logging.debug('r=%d c=%d [%d:%d, %d:%d] %f',
                              rnum, cnum,
                              rnum, rnum + pattern_width,
                              cnum, cnum + pattern_width,
                              product)
                """

                # store the convolution product
                cp_image[rnum, cnum] = product

        logging.debug('========= end of convolution. Start get peaks')

        peaks = region

        # make the CP threshold above the background fluctuations
        cp_threshold *= 1.3

        # print("cp_threshold", cp_threshold)

        self.cluster_dict = dict()

        #
        # scan the convolution image to detect peaks and get all clusters
        #
        for r, row in enumerate(cp_image[half:-half, half:-half]):
            # print('2) rnum=', rnum)
            for c, col in enumerate(row):

                rnum = r + half
                cnum = c + half

                if cp_image[rnum, cnum] > cp_threshold:
                    """
                    rnum, cnum is the center of the convolution zone

                    check if we have a peak centered at this position:
                    - the CP at the center of the zone must be higher then any CP immediately around the center
                    """
                    peak = self.has_peak(cp_image, rnum, cnum)
                    if peak:
                        #
                        # if a peak is detected, we get the cluster
                        #
                        # print('peak at [%d %d]' % (rnum, cnum))
                        x = 3

                        peaks[rnum - x:rnum + x + 1, cnum] = region[rnum, cnum]
                        peaks[rnum, cnum - x:cnum + x + 1] = region[rnum, cnum]

                        integral, radius = self.get_peak(cp_image, rnum, cnum)
                        if radius > 1:
                            # print('peak at [%d %d] %f' % (rnum, cnum, integral, ))
                            self.cluster_dict[integral] = {'r':rnum, 'c':cnum, 'integral':integral, 'top':self.region[rnum, cnum], 'radius':radius, 'cp':cp_image[rnum, cnum]}

        logging.debug('========= end of get peaks. Store clusters')

        self.clusters = []
        for key in sorted(self.cluster_dict.keys(), reverse=True):
            c = self.cluster_dict[key]
            self.clusters.append(c)

            # print(repr(c))
            rnum = c['r']
            cnum = c['c']
            radius = c['radius']
            cp_image[rnum-radius:rnum+radius+1, cnum-radius:cnum+radius+1] = 12.

        return pattern, cp_image, peaks

    def run_recursive(self, threshold=None):
        """ 
        procedure to construct all clusters above a given threshold 
        using a recursive algorithm
        """
        if threshold is not None:
            self.threshold = threshold

        self.done = np.zeros_like(self.region)
        self.below = self.region < self.threshold
        self.image = np.zeros_like(self.region)
        self.max = np.max(self.region)
        self.clusters = []
        self.cluster_dict = dict()

        cluster_id = 1
        for rnum, row in enumerate(self.region):
            for cnum, _ in enumerate(row):

                cluster = TCluster(cluster_id)
                try:
                    self.recursive_build_cluster(rnum, cnum, obj=cluster)
                except RuntimeError as ex:
                    logging.error(ex)

                if cluster.integral > 0:
                    # we store only non empty clusters
                    self.clusters.append(cluster)
                    self.cluster_dict['%f %f', cluster.centroid[1], cluster.centroid[0]] = cluster
                cluster_id += 1

        self.clusters.sort(key=lambda cluster: cluster.integral, reverse=True)

        logging.debug('%d clusters: %s', len(self.clusters),
                      ','.join(['%d' % len(cl.pixels) for cl in self.clusters]))

    def one_pixel(self, rnum, cnum, cluster_id):
        # time.sleep(0.1)

        # at least we skip useless pixels

        # in principle we don' need lock
        # with LockContext(self.region_lock):

        if self.done[rnum, cnum] > 0:
            return False
        if self.below[rnum, cnum]:
            return False

        # this pixel has to be considered
        try:
            # we create a TClusterFactory
            # even if in the meantime, it has become useless because this pixel was already used
            factory = TClusterFactory(self, rnum, cnum, cluster_id, self.trace)
            # an empty cluster has been created => lets's store it
            self.cluster_dict[cluster_id] = factory.cluster
            # run the clustering from this pixel
            factory.start()
            return True
        except RuntimeError as ex:
            logging.error(ex)
            return False

    def run_threaded(self, threshold=None):
        """ procedure to construct all clusters above a given threshold """

        global drawer
        global myregion

        if threshold is not None:
            self.threshold = threshold

        self.done = np.zeros_like(self.region)
        self.below = self.region < self.threshold
        self.image = np.zeros_like(self.region)
        self.max = np.max(self.region)
        self.clusters = []
        self.cluster_dict = dict()

        self.trace = np.zeros_like(self.region)     # a temp array to mark pixels already accessed

        if drawer is not None:
            drawer.change_image(self.trace)

        # now start the linear image grid scan
        strategy = mystrategy

        runner = RegionRunner(self, strategy)
        runner.start()

        return

    def find_clusters(self, x0, y0, radius):
        '''
        :param x0:
        :param y0:
        :param radius:
        :return:
        '''
        results = []
        for x in range(radius*2):
            for y in range(radius*2):
                # coord = '%f %f', x + x0 - radius, y + y0 - radius
                coord = "[%f %f]" % (x + x0 - radius, y + y0 - radius)
                if coord in self.cluster_dict:
                    cluster = self.cluster_dict[coord]
                    results.append(cluster)

        return results

def tests():
    'Unit tests'
    return 0

if __name__ == '__main__':
    sys.exit(tests())

