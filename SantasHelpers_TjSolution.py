""" Simple solution to the Santa 2014 Kaggle competition evaluation metric.
This solution takes each toy in turn (in chronological order) and assigns the next
available elf to it. """
__author__ = 'Tommie Jones'
__date__ = 'Dec. 7, 2014'

import os
import gc
import csv
import math
import heapq
import time
import datetime

from hours import Hours
from toy import Toy
from elf import Elf

# ========================================================================== #

def create_elves(NUM_ELVES):
    """ Elves are stored in a sorted list using heapq to maintain their order by next available time.
    List elements are a tuple of (next_available_time, elf object)
    :return: list of elves
    """
    list_elves = []
    for i in xrange(1, NUM_ELVES+1):
        elf = Elf(i)
        heapq.heappush(list_elves, (elf.next_available_time, elf))
    return list_elves


def assign_elf_to_toy(input_time, current_elf, current_toy, hrs):
    """ Given a toy, assigns the next elf to the toy. Computes the elf's updated rating,
    applies the rest period (if any), and sets the next available time.
    :param input_time: list of tuples (next_available_time, elf)
    :param current_elf: elf object
    :param current_toy: toy object
    :param hrs: hours object
    :return: list of elves in order of next available
    """
    start_time = hrs.next_sanctioned_minute(input_time)  # double checks that work starts during sanctioned work hours
    duration = int(math.ceil(current_toy.duration / current_elf.rating))
    sanctioned, unsanctioned = hrs.get_sanctioned_breakdown(start_time, duration)

    if unsanctioned == 0:
        return hrs.next_sanctioned_minute(start_time + duration), duration
    else:
        return hrs.apply_resting_period(start_time + duration, unsanctioned), duration

def find_closest_idx(toy_list, target):
    start = 0
    end = len(toy_list)
    i = 0
    if (toy_list[0].duration  > target):
        print 'Bottomed Out'
        return len(toy_list) - 1
    while True:
        i = ( (end - start) / 2 ) + start
        if (i == start):
            return i
        if (i == end):
            return i
        if (toy_list[i].duration <=target) and (toy_list[i-1].duration >= target):
            print "XXXX"
            return i
        if (toy_list[i].duration > target):
            end = i
        else:
            start = i

def solution_firstAvailableElf(toy_file, soln_file, myelves):
    """ Creates a simple solution where the next available elf is assigned a toy. Elves do not start
    work outside of sanctioned hours.
    :param toy_file: filename for toys file (input)
    :param soln_file: filename for solution file (output)
    :param myelves: list of elves in a priority queue ordered by next available time
    :return:
    """
    hrs = Hours()
    ref_time = datetime.datetime(2014, 1, 1, 0, 0)
    row_count = 0
    toy_list = []
    loop_count = 0

    #Build list of toys
    with open(toy_file, 'rb') as f:
        toysfile = csv.reader(f)
        toysfile.next()  # header row
        for row in toysfile:
            current_toy = Toy(row[0], row[1], row[2])
            toy_list.append(current_toy)

    sorted_toy_list = sorted(toy_list,key = lambda e: e.duration)
    toy_list = None
    gc.collect()

    print 'All is sorted:'

    with open(soln_file, 'wb') as w:
        wcsv = csv.writer(w)
        wcsv.writerow(['ToyId', 'ElfId', 'StartTime', 'Duration'])
        while len(sorted_toy_list) > 0:
            elf_available_time, current_elf = heapq.heappop(myelves)
            if current_elf.rating > 3.9:
                current_toy = sorted_toy_list.pop()
                print 'Elf {0} eff {1} toy {2} duration {3} BIG TOY---------------------------------'.format(current_elf.id, current_elf.rating, current_toy.id, current_toy.duration)
                loop_count = loop_count + 1
            else:
                val = hrs.get_sanctioned_time_left(elf_available_time)
                current_toy_idx = find_closest_idx(sorted_toy_list, current_elf.rating * (val*1.15))
                current_toy = sorted_toy_list.pop(current_toy_idx)
                if len(sorted_toy_list) % 10 == 0:
                    print 'Elf {0} eff {1} toy {2} duration {3} SMALL TOY {4}> {5}'.format(current_elf.id, current_elf.rating, current_toy.id, current_toy.duration, len(sorted_toy_list), len(sorted_toy_list))

            # get next available elf

            work_start_time = elf_available_time

            #!# work_start_time cannot be before toy's arrival
            #!if work_start_time < current_toy.arrival_minute:
            #!    print 'Work_start_time before arrival minute: {0}, {1}'.\
            #!        format(work_start_time, current_toy.arrival_minute)
            #!    exit(-1)

            current_elf.next_available_time, work_duration = \
                assign_elf_to_toy(work_start_time, current_elf, current_toy, hrs)
            current_elf.update_elf(hrs, current_toy, work_start_time, work_duration)

            # put elf back in heap
            heapq.heappush(myelves, (current_elf.next_available_time, current_elf))

            # write to file in correct format
            tt = ref_time + datetime.timedelta(seconds=60*work_start_time)
            time_string = " ".join([str(tt.year), str(tt.month), str(tt.day), str(tt.hour), str(tt.minute)])
            wcsv.writerow([current_toy.id, current_elf.id, time_string, work_duration])
    print 'loop_count = {0}'.format(loop_count)


# ======================================================================= #
# === MAIN === #

if __name__ == '__main__':

    start = time.time()

    NUM_ELVES = 900

    toy_file = os.path.join(os.getcwd(), 'toys_rev2.csv')
    soln_file = os.path.join(os.getcwd(), 'TJ1Submission_rev2.csv')

    myelves = create_elves(NUM_ELVES)
    solution_firstAvailableElf(toy_file, soln_file, myelves)

    print 'total runtime = {0}'.format(time.time() - start)
