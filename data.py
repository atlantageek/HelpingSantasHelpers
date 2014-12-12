import os
import sys
import csv
import random
import math

def load_toys(toy_file):
    output = []

    with open(toy_file, 'rb') as f:
        toy_file = csv.reader(f)
        toy_file.next()  # header row
        output = sorted([toy for toy in toy_file], key = lambda t: t[2])

    return output

def mean(toys):
    return sum((int(toy[2]) for toy in toys)) / float(len(toys))

def median(toys):
    midp = len(toys) / 2
    if len(toys) % 2 == 1:
        return (int(toys[midp][2]) + int(toys[midp + 1][2])) / 2.0
    else:
        return int(toys[midp][2])

def stdev(toys):
    m = mean(toys)

    return (sum((int(toy[2]) - m) ** 2 for toy in toys) / float(len(toys))) ** 0.5

def sample(toy_file, output_filename, sample_size):
    unsampled = load_toys(toy_file)
    sample = sorted(random.sample(unsampled, sample_size), key = lambda toy: toy[2])

    with open(output_filename, 'wb') as f:
        wcsv = csv.writer(f)
        wcsv.writerow(['ToyId', 'Arrival_time', 'Duration'])

        ctr = 0
        for toy in sample:
            wcsv.writerow(toy)
            ctr += 1
            if ctr % 1000 == 0:
                print "... wrote %d lines of the sample" % (ctr)

    print "Done writing file to %s." % (output_filename)

    return sample, unsampled

ifname = sys.argv[1]
ofname = sys.argv[2]
ssize  = int(sys.argv[3])

toys, all_toys = sample(ifname, ofname, ssize)

print
print "statistics about sample file:"
print "   mean: %0.4f" % (mean(toys))
print " median: %0.1f" % (median(toys))
print "std dev: %0.4f" % (stdev(toys))
print
print
print "statistics about unsampled file:"
print "   mean: %0.4f" % (mean(all_toys))
print " median: %0.1f" % (median(all_toys))
print "std dev: %0.4f" % (stdev(all_toys))
print
