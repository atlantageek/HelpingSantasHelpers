import sys
import random

from SantasHelperSolution import *

class SantasHelperSolutionDynamicProgramming(SantasHelperSolution):
    def run(self):
        while len(self.toys) > 0:
            start_time, elf = self.next_available_elf()

            toy = self.toys.pop(random.randint(0, len(self.toys) - 1))

            self.record_work(elf, toy)


input_file = sys.argv[1]
output_file = sys.argv[2]
num_elves = int(sys.argv[3])

solution = SantasHelperSolutionDynamicProgramming(input_file, output_file, num_elves)
solution.process()
