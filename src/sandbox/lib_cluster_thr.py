#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Search clusters in images.
'''

import sys
import numpy as np
import threading, time, random
import matplotlib.pyplot as plt
from lib_logging import logging
from lib_cluster import *


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

class ClusterThr(Cluster):

    def __init__(self, cluster_id, trace=None):

        Cluster.__init__(self)

        self.id = cluster_id
        self.integral = 0
        self.centroid = None
        self.min_row = None
        self.max_row = None
        self.min_column = None
        self.max_column = None
        self.centroid = None
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

        global total_pixels
        global drawer

        # Do not penalize non-threaded version
        if drawer is not None and threading.active_count() > 1:
            total_pixels += 1

            drawer.redraw(column, row, 1500 * self.id)

            time.sleep(sleep_in_cluster)

        Cluster.add(self,row,column,value)

        # FIXME: THIS COMPUTING OF THE CENTROID IS NOT USED ANY MORE IN
        # THE NEW IMPLEMENTATION

        self.min_max('row', row)
        self.min_max('column', column)

        centroid_row = (self.min_row+self.max_row)/2.0
        centroid_column = (self.min_column+self.max_column)/2.0
        self.centroid = (centroid_row, centroid_column)

        self.integral += value


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

class LockContext(object):
    def __init__(self, lock):
        self.lock = threading.Lock()
    def __enter__(self):
        self.lock.acquire()
        return self.lock
    def __exit__(self, type, value, traceback):
        self.lock.release()

class ClusterFactory(threading.Thread):
    def __init__(self, region, row, column, cluster_id, trace=None):
        threading.Thread.__init__(self)

        self.threadID = cluster_id
        self.name = 'c%d' % cluster_id

        self.region = region
        self.shape = region.shape
        self.row = row
        self.column = column
        self.cluster = ClusterThr(cluster_id, trace)
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

class RegionThr(Region):

    # pylint: disable=too-many-instance-attributes

    def __init__(self, region, threshold):

        logging.debug('Region> threshold {}'.format(threshold))
        Region.__init__(self, region, threshold)

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

                cluster = ClusterThr(cluster_id)
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
            # we create a ClusterFactory
            # even if in the meantime, it has become useless because this pixel was already used
            factory = ClusterFactory(self, rnum, cnum, cluster_id, self.trace)
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

def tests():
    'Unit tests'
    return 0

if __name__ == '__main__':
    sys.exit(tests())

