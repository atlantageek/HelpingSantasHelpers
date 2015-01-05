import os
import sys
import gc
import csv
import math
import heapq
import time
import datetime
import string
import logging

from hours import Hours
from toy import Toy
from elf import Elf

NUM_ELVES = 900

class SantasHelperSolution:
    def __init__(self, toy_filename, output_filename, total_elves = NUM_ELVES):
        self.total_elves     = total_elves
        self.toy_filename    = toy_filename
        self.output_filename = output_filename

        self.base_time = datetime.datetime(2014, 1, 1, 0, 0)
        self.hours = Hours()
        self._init_elves()
        self._init_toys()

    def process(self):
        self.run()
        self._open_output_file().close()
        self._open_output_stats_file().close()

    def run(self):
        raise Exception("Not implemented.")

    def _init_elves(self):
        self.elves = []
        self._elves = []
        self.elves_by_id = [None] * (self.total_elves + 1)
        self.elves_by_id[0] = {}
        for i in xrange(self.total_elves):
            elf = Elf(i + 1)
            self.elves_by_id[i + 1] = elf
            heapq.heappush(self.elves, (elf.next_available_time, elf))
            self._elves.append(elf)

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
        if not hasattr(self, 'ofile') or self.ofile.closed == True:
            self.ofile = open(self.output_filename, 'wb')
        return self.ofile

    def _open_output_stats_file(self):
        if not hasattr(self, 'stats_file') or self.stats_file.closed == True:
            self.stats_file = open(string.replace(self.output_filename, ".", "_stats."), 'wb')
        return self.stats_file

    def _csv_writer(self):
        if not hasattr(self, 'csv_writer'):
            self.csv_writer = csv.writer(self._open_output_file())
            self.csv_writer.writerow(['ToyId', 'ElfId', 'StartTime', 'Duration'])
        return self.csv_writer

    def _csv_stats_writer(self):
        if not hasattr(self, 'csv_stats_writer'):
            self.csv_stats_writer = csv.writer(self._open_output_stats_file())
            self.csv_stats_writer.writerow(['ToyId', 'ElfId', 'StartTime', 'Duration', 'ElfProductivity', 'ToyDuration', 'Median'])
        return self.csv_stats_writer

    def next_available_elf(self):
        return heapq.heappop(self.elves)

    def get_elf_productivity_position(self,elf):
        productivity_target = elf.rating
        i=0
        for target_elf in self._elves:
            if productivity_target < target_elf.rating:
                i += 1
        return i

    def return_elf(self, elf):
        heapq.heappush(self.elves, (elf.next_available_time, elf))

    def record_work(self, elf, toy):
        start_time = elf.next_available_time
        productivity = elf.rating

        elf.next_available_time, work_duration = self.assign_elf_to_toy(start_time, elf, toy)
        elf.update_elf(self.hours, toy, start_time, work_duration)

        tt = self.base_time + datetime.timedelta(seconds = 60 * start_time)
        time_string = " ".join([str(tt.year), str(tt.month), str(tt.day), str(tt.hour), str(tt.minute)])
        timestamp = str(tt)
        self._csv_writer().writerow([toy.id, elf.id, time_string, work_duration])

        if 0 == len(self.toys):
           center = 0
        else:
           center = self.toys[len(self.toys)/2].duration
        self._csv_stats_writer().writerow([toy.id, elf.id, timestamp, work_duration, productivity, toy.duration, center])
        

        return elf, timestamp, tt + datetime.timedelta(seconds = 60 * work_duration)

    def record_work_starting_later_than(self, elf, toy, start_time):
        start_time = max(elf.next_available_time, start_time)
        productivity = elf.rating

        elf.next_available_time, work_duration = self.assign_elf_to_toy(start_time, elf, toy)
        elf.update_elf(self.hours, toy, start_time, work_duration)

        tt = self.base_time + datetime.timedelta(seconds = 60 * start_time)
        time_string = " ".join([str(tt.year), str(tt.month), str(tt.day), str(tt.hour), str(tt.minute)])
        timestamp = str(tt)
        self._csv_writer().writerow([toy.id, elf.id, time_string, work_duration])
        self._csv_stats_writer().writerow([toy.id, elf.id, timestamp, work_duration, productivity, toy.duration])

        return elf, timestamp, tt + datetime.timedelta(seconds = 60 * work_duration)

    def assign_elf_to_toy(self, work_start_time, elf, toy):
        start_time = self.hours.next_sanctioned_minute(work_start_time)
        duration = int(math.ceil(toy.duration / elf.rating))
        sanctioned, unsanctioned = self.hours.get_sanctioned_breakdown(start_time, duration)

        if unsanctioned == 0:
            return self.hours.next_sanctioned_minute(start_time + duration), duration
        else:
            return self.hours.apply_resting_period(start_time + duration, unsanctioned), duration

    def calc_rating(self, duration, sanctioned_time, current_rating):
      #Assume duration/current_rating > sanctioned_time
        work_time = duration/current_rating
        unsanctioned = work_time - sanctioned_time
        sanctioned = sanctioned_time
        future_rating = max(0.25, min(4.0, current_rating * (1.02 ** (sanctioned/60.0)) *
                              (0.9 ** (unsanctioned/60.0))))
        return future_rating


    def find_best_fit(self, current_rating, time_left, start_idx):
        last_duration = self.toys[len(self.toys) - 1].duration
        previous_time_change = 0
        #logging.info("Searching .... {0}".format(start_idx)) 
        best_idx= -1
        best_rating = 1000000000
        for idx in range( start_idx,len(self.toys)-1):
            trial_duration = self.toys[idx].duration
            future_rating1 = self.calc_rating(trial_duration, time_left , current_rating)
            future_rating2 = self.calc_rating(last_duration, time_left , current_rating)
            time_change = trial_duration / current_rating + last_duration /future_rating1 - last_duration/current_rating - trial_duration/future_rating2
            if time_change < best_rating:
                #logging.info("{0} Found {1} {3} -> {2} {4}".format(  start_idx, idx - 1, idx, previous_time_change, time_change))
                best_rating = time_change
                best_idx = idx
                #logging.info( "{0} {1} {2}".format(best_rating, time_change, best_idx))
                #logging.info("{0} Found {1} {2} ".format(  start_idx, idx ,  time_change))
            previous_time_change = time_change
        #logging.info(best_idx) 
        #logging.info("===========")
        return best_idx

    def closest_toy_with_duration(self, duration):
        idx = self._binary_search_toys(duration)
        return self.toys.pop(idx)

    def closest_toy_with_duration_idx(self, duration):
        idx = self._binary_search_toys(duration)
        return idx

    def _binary_search_toys(self, duration):
        start = 0
        end = len(self.toys)

        if (self.toys[0].duration > duration):
            return 0

        while True:
            if start >= end - 1:
                return start

            idx = int(math.floor((end - start) / 2.0)) + start

            if self.toys[idx].duration < duration:
                start = idx
            elif self.toys[idx].duration > duration:
                end = idx
            else:
                return idx

    def average_productivity(self):
        total_rating = sum((elf.rating for elf in self._elves))
        return total_rating / float(len(self._elves))

    def work_remaining(self):
        return sum((toy.duration for toy in self.toys))

    def _search_toys_id(self, target_id):
        idx = 0
        end = len(self.toys)
        print end
        while idx < len(self.toys):
           id =  self.toys[idx].id
           if self.toys[idx].id == target_id:
               print idx
               return idx
           idx += 1
        print 'Fail'
        return -1
