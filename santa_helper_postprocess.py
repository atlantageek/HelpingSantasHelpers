import sys
from SantasHelperSolution import *
solution = []
class SantasHelperSolutionNaive(SantasHelperSolution):
    def run(self):
        target_rating = 0.40
        while len(self.toys) > 0:
            start_time, elf = self.next_available_elf()

            time_left = self.hours.get_sanctioned_time_left(start_time)
            toy_idx = self.closest_toy_with_duration_idx(elf.rating * time_left * 1.01)
            size = 1
            if self.toys[len(self.toys) - 1].duration > 18000:
                target_rating = 0.4
            else:
                target_rating = 0.30

            if elf.rating > target_rating:
                if self.toys[toy_idx].duration < 240:
                    #Small optimization.  Look at all the leves that are about to finish and find where this elf's productivity is compared to the others.
                    #If its the 4th (for example) most productive elf then get the 4th biggest toy leaving the bigger toys to the other elves.
                    idx = self.get_elf_productivity_position(elf)
                    toy_idx = (idx + 1) * -1
                    toy = self.toys.pop( toy_idx)
                   # toy = self.toys.pop()
                    print 'Elf {0} eff {1} toy {2} duration {3} Big TOY[{4}] {5} {6}'.format(elf.id, elf.rating, toy.id, toy.duration, len(self.toys), elf.rating, toy_idx)
                    size=3
                else:
                    toy = self.toys.pop(toy_idx)
                    print 'Elf {0} eff {1} toy {2} duration {3} MEDIUM TOY[{4}]'.format(elf.id, elf.rating, toy.id, toy.duration, len(self.toys))
                    size=2
            else:
                toy = self.toys.pop(toy_idx)
                print 'Elf {0} eff {1} toy {2} duration {3} SMALL TOY[{4}]'.format(elf.id, elf.rating, toy.id, toy.duration, len(self.toys))
                size=1
            productivity = elf.rating
            elf, last_work_started, last_work_ended = self.record_work(elf, toy)
            self.return_elf(elf)
            solution.append({'elf_id':elf.id, 'toy_id':toy.id,'size':size, 'productivity': productivity, 'duration': toy.duration})

class SantasOrderedSolutionNaive(SantasHelperSolution):
    def run(self):
        target_rating = 0.4
        while len(self.toys) > 0:
            sol=solution.pop(0)
            elf = self.elves_by_id[sol['elf_id']]
            start_time = elf.next_available_time
            print sol['toy_id']
            toy_idx = self._search_toys_id(sol['toy_id'])
            toy = self.toys.pop(toy_idx)
            print 'toy {0} duration {1}'.format(toy.id, toy.duration)

            elf, last_work_started, last_work_ended = self.record_work(elf, toy)
            self.return_elf(elf)


def reorder_solution():
    print "STARTING REORDER"
    for idx in range(0,len(solution) - 2):
       if solution[idx]['size'] == 3:
         print 'IDX {0}   '.format(idx)
         for idx2 in range(idx + 1, len(solution) - 1):
           if solution[idx]['elf_id'] == solution[idx2]['elf_id'] and solution[idx2]['size'] == 3:
               if solution[idx]['productivity'] > solution[idx2]['productivity']:
                   if solution[idx]['duration'] < solution[idx2]['duration']:
                      print 'Toy{4},{5}productivity {0} > {1} duration {2} < {3}'.format(solution[idx]['productivity'], solution[idx2]['productivity'], solution[idx]['duration'], solution[idx2]['duration'], solution[idx]['toy_id'], solution[idx2]['toy_id'])
                      productivity1 = solution[idx]['productivity']
                      productivity2 = solution[idx2]['productivity']
                      temp = solution[idx]
                      solution[idx] = solution[idx2]
                      solution[idx2] = temp
                      solution[idx]['productivity'] = productivity1
                      solution[idx2]['productivity'] = productivity2
                      print 'Fixed productivity {0} < {1} duration {2} < {3}'.format(solution[idx]['productivity'], solution[idx2]['productivity'], solution[idx]['duration'], solution[idx2]['duration'])
                      print 'swap1'
               if solution[idx]['productivity'] < solution[idx2]['productivity']:
                   if solution[idx]['duration'] > solution[idx2]['duration']:
                      print 'Toy{4},{5} productivity {0} < {1} duration {2} > {3}'.format(solution[idx]['productivity'], solution[idx2]['productivity'], solution[idx]['duration'], solution[idx2]['duration'], solution[idx]['toy_id'],solution[idx2]['toy_id'])
                      productivity1 = solution[idx]['productivity']
                      productivity2 = solution[idx2]['productivity']
                      temp = solution[idx]
                      solution[idx] = solution[idx2]
                      solution[idx2] = temp
                      solution[idx]['productivity'] = productivity1
                      solution[idx2]['productivity'] = productivity2
                      print 'Fixed productivity {0} > {1} duration {2}> {3}'.format(solution[idx]['productivity'], solution[idx2]['productivity'], solution[idx]['duration'], solution[idx2]['duration'])
                      print 'swap2'


input_file = sys.argv[1]
output_file = sys.argv[2]
num_elves = int(sys.argv[3])

naive = SantasHelperSolutionNaive(input_file, output_file, num_elves)
naive.process()
#Disable postprocess. (Cause it doesnt work.)
#reorder_solution()
#post_process = SantasOrderedSolutionNaive(input_file, 'step2_' + output_file, num_elves)
#post_process.process()
