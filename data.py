import os
import sys
import csv
import math

def load_toys(toy_file):
    output = []

    with open(toy_file, 'rb') as f:
        toy_file = csv.reader(f)
        toy_file.next()  # header row
        output = sorted([int(toy[2]) for toy in toy_file])

    return output

def analyze(toys):
    sizes = { 10: 0, 30: 0, 60: 0, 120: 0, 300: 0, 600: 0, 1000000: 0 }
    cumulative_durations = { 10: 0, 30: 0, 60: 0, 120: 0, 300: 0, 600: 0, 1000000: 0 }

    for toy in toys:
        for key in sizes.keys():
            if toy <= key:
                sizes[key] = sizes[key] + 1
                cumulative_durations[key] = cumulative_durations[key] + toy

    return sizes, cumulative_durations

tfname = sys.argv[1]
print "Loading %s..." % (tfname)

toys = load_toys(tfname)
print "%d total toys found" % (len(toys))

sizes, cumulative_durations = analyze(toys)
print(sizes)
print(cumulative_durations)
