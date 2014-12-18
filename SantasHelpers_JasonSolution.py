""" Simple solution to the Santa 2014 Kaggle competition evaluation metric.
This solution takes each toy in turn (in chronological order) and assigns the next
available elf to it. """
__author__ = 'Tommie Jones'
__date__ = 'Dec. 7, 2014'

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
    #if (toy_list[0].duration  > target):
    #    print 'Bottomed Out'
    #    return len(toy_list) - 1
    while True:
        i = ( (end - start) / 2 ) + start
        if (i == start):
            return i
        if (i == end):
            return i
        if (toy_list[i].duration >= target) and (toy_list[i-1].duration < target):
            return i - 1
        if (toy_list[i].duration > target):
            end = i
        else:
            start = i

#def center_of_mass(toy_list):
#    big_idx = find_closest_idx(toy_list,2500)
#    small_idx = find_closest_idx(toy_list,600)
#    small_wgt_sum = reduce(lambda x,y: x + y.duration)
#    toy_len = len(toy_list)


def solution_firstAvailableElf(toy_file, soln_file, myelves, threshold, over_factor):
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
        wcsv.writerow(['ToyId', 'ElfId', 'StartTime', 'Duration', 'Productivity', 'Base Duration'])
        while len(sorted_toy_list) > 0:
            elf_available_time, current_elf = heapq.heappop(myelves)
            val = hrs.get_sanctioned_time_left(elf_available_time)
            target_rating = 0.4
            if current_elf.rating >= target_rating:
                current_toy_idx = find_closest_idx(sorted_toy_list, current_elf.rating * (val*1.1))
                if sorted_toy_list[current_toy_idx].duration > (600 * target_rating):
                    current_toy = sorted_toy_list.pop(current_toy_idx)
                    print 'Elf {0} eff {1} toy {2} duration {3}/{5} MEDIUM TOY-----{4}-'.format(current_elf.id, current_elf.rating, current_toy.id, current_toy.duration, len(sorted_toy_list), current_elf.rating * val * 1.15)
                else:
                    current_toy = sorted_toy_list.pop(-1 )
                    print 'Elf {0} eff {1} toy {2} duration {3} BIG TOY----{4}---'.format(current_elf.id, current_elf.rating, current_toy.id, current_toy.duration, len(sorted_toy_list))
                loop_count = loop_count + 1
                #current_elf.rating_target = max(current_elf.rating_target - threshold,0.3)
            else:
                current_toy_idx = find_closest_idx(sorted_toy_list, current_elf.rating * (val*1.01))
                current_toy = sorted_toy_list.pop(current_toy_idx)
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
            productivity = current_elf.rating
            current_elf.update_elf(hrs, current_toy, work_start_time, work_duration)

            # put elf back in heap
            heapq.heappush(myelves, (current_elf.next_available_time, current_elf))

            # write to file in correct format
            tt = ref_time + datetime.timedelta(seconds=60*work_start_time)
            time_string = " ".join([str(tt.year), str(tt.month), str(tt.day), str(tt.hour), str(tt.minute)])
            wcsv.writerow([current_toy.id, current_elf.id, time_string, work_duration, productivity, current_toy.duration])
    print 'loop_count = {0}'.format(loop_count)
    return work_start_time


# ======================================================================= #
# === MAIN === #

if __name__ == '__main__':

    start = time.time()

    NUM_ELVES = 9

    toy_file = os.path.join(os.getcwd(), 'toys_sample1.csv')
    dataset = os.path.join(os.getcwd(), 'result.csv')

    with open(dataset, 'wb') as w:
        wcsv = csv.writer(w)
        wcsv.writerow(['Threshold', 'Over Factor', 'Last Start Time'])
        threshold_list = [0.02]
        for threshold in threshold_list:
            soln_file = os.path.join(os.getcwd(), 'p' + str(threshold) + '.csv')
            myelves = create_elves(NUM_ELVES)
            start_time = solution_firstAvailableElf(toy_file, soln_file, myelves, threshold, 1.02)
            wcsv.writerow([threshold, start_time])

    print 'total runtime = {0}'.format(time.time() - start)
