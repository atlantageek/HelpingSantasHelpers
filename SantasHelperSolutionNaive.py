import sys
from SantasHelperSolution import *

class SantasHelperSolutionNaive(SantasHelperSolution):
    def run(self):
        while len(self.toys) > 0:
            start_time, elf = self.next_available_elf()

            if elf.rating > 3.9:
                toy = self.toys.pop()
            else:
                time_left = self.hours.get_sanctioned_time_left(start_time)
                toy = self.closest_toy_with_duration(elf.rating * time_left * 1.15)

            self.record_work(elf, toy)

            if len(self.toys) % 1000 == 0:
                print "Average productivity: %0.4f | Work remaining: %0.4f" % (self.average_productivity(), self.work_remaining())

input_file = sys.argv[1]
output_file = sys.argv[2]
num_elves = int(sys.argv[3])

naive = SantasHelperSolutionNaive(input_file, output_file, num_elves)
naive.process()
