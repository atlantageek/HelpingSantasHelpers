import os
import sys
import gc
import csv
import math
import heapq
import time
import datetime

from hours import Hours
from toy import Toy
from elf import Elf

NUM_ELVES = 900

class SantaHelpersSolution:
    def __init__(self, toy_filename, output_filename, total_elves = NUM_ELVES):
        self.total_elves     = total_elves
        self.toy_filename    = toy_filename
        self.output_filename = output_filename

        self._init_elves()
        self._init_toys()

    def _init_elves(self):
        self.elves = []
        for i in xrange(self.total_elves):
            elf = Elf(i + 1)
            heapq.heappush(self.elves, (elf.next_available_time, elf))

    def _init_toys(self):
        _toys = []
        with open(self.toy_filename, 'rb') as f:
            toysfile = csv.reader(f)
            toysfile.next()  # header row
            _toys = [Toy(row[0], row[1], row[2]) for row in toysfile]


        self.toys = sorted(_toys, key = lambda toy: toy.duration)

        _toys = None
        gc.collect()

    def _open_output_file(self):
        if hasattr(self, 'ofile') and ofile.closed == False:
            return self.ofile
        else:
            self.ofile = open(self.output_filename, 'wb')

    def _csv_writer(self):
        if !hasattr(self, 'csv_writer'):
            self.csv_writer = csv.writer(self._open_output_file())
        return self.csv_writer

    def next_available_elf(self):
        return heapq.heappop(self.elves)

    def return_elf(self, elf):
        heapq.heappush(self.elves, (elf.next_available_time, elf))

    def record_work(self, elf, toy, duration, start_time = None):
        if start_time is None:
            start_time = elf.available_time

        tt = ref_time + datetime.timedelta(seconds = 60 * start_time)
        timestamp = " ".join([str(tt.year), str(tt.month), str(tt.day), str(tt.hour), str(tt.minute)])
        self._csv_writer().writerow([toy.id, elf.id, timestamp, duration])
