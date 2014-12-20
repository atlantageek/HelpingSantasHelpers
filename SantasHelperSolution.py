import os
import sys
import gc
import csv
import math
import heapq
import time
import datetime
import string

from hours import Hours
from toy import Toy
from elf import Elf

NUM_ELVES = 900

class SantasHelperSolution:
    def __init__(self, toy_filename, output_filename, total_elves = NUM_ELVES):
        self.total_elves     = total_elves
        self.toy_filename    = toy_filename
        self.output_filename = output_filename

        self.hours = Hours()
        self._init_elves()
        self._init_toys()

    def run(self):
        raise Exception("Not implemented.")

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
        if hasattr(self, 'ofile') and self.ofile.closed == False:
            return self.ofile
        else:
            self.ofile = open(self.output_filename, 'wb')

    def _open_output_stats_file(self):
        if hasattr(self, 'stats_file') and self.stats_file.closed == False:
            return self.stats_file
        else:
            self.stats_file = open(string.replace(self.output_filename, ".", "_stats."), 'wb')

    def _csv_writer(self):
        if not hasattr(self, 'csv_writer'):
            self.csv_writer = csv.writer(self._open_output_file())
            self.csv_writer.writerow(['ToyId', 'ElfId', 'StartTime', 'Duration'])
        return self.csv_writer

    def _csv_stats_writer(self):
        if not hasattr(self, 'csv_stats_writer'):
            self.csv_stats_writer = csv.writer(self._open_output_stats_file())
            self.csv_stats_writer.writerow(['ToyId', 'ElfId', 'StartTime', 'Duration', 'ElfProductivity', 'ToyDuration'])
        return self.csv_stats_writer

    def next_available_elf(self):
        return heapq.heappop(self.elves)

    def return_elf(self, elf):
        heapq.heappush(self.elves, (elf.next_available_time, elf))

    def record_work(self, elf, toy, duration):
        start_time = elf.available_time

        productivity = elf.rating

        elf.next_available_time, work_duration = self.assign_elf_to_toy(work_start_time, elf, toy)
        elf.update_elf(hours, toy, work_start_time, work_duration)

        self.return_elf(elf)

        tt = ref_time + datetime.timedelta(seconds = 60 * start_time)
        time_string = " ".join([str(tt.year), str(tt.month), str(tt.day), str(tt.hour), str(tt.minute)])
        timestamp = str(tt)
        self._csv_writer().writerow([toy.id, elf.id, time_string, duration])
        self._csv_stats_writer().writerow([toy.id, elf.id, timestamp, duration, productivity, toy.duration])

        return timestamp

    def assign_elf_to_toy(work_start_time, elf, toy):
        start_time = hours.next_sanctioned_minute(input_time)
        duration = int(math.ceil(toy.duration / elf.rating))
        sanctioned, unsanctioned = hours.get_sanctioned_breakdown(start_time, duration)

        if unsanctioned == 0:
            return hours.next_sanctioned_minute(start_time + duration), duration
        else:
            return hours.apply_resting_period(start_time + duration, unsanctioned), duration
