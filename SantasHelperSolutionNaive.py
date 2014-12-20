from SantasHelperSolution import *

class SantasHelperSolutionNaive(SantasHelperSolution):
    def run(self):
        while len(self.toys) > 0:
            start_time, elf = self.next_available_elf()

            if elf.rating > 3.9:
                toy = self.toys.pop()
            else:
                time_left = self.hours.get_sanctioned_time_left(start_time)
                toy_idx = find_closest_idx(elf.rating * time_left * 1.15)
                toy = self.toys.pop(toy_idx)
