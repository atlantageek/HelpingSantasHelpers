import sys
import logging
reload(logging)
logging.basicConfig(format = u'[%(asctime)s]  %(message)s', level = logging.INFO)
from SantasHelperSolution import *
solution = []
#The leftovers are at 2810 - 9410 Year 2397
class SantasHelperSolutionNaive(SantasHelperSolution):
    def get_target(self,biggest):
        return min(0.4125, max((float(biggest - 7100) / 100000.0) + 0.25,0.255))
    def run(self):
        target_rating = 0.41
        while len(self.toys) > 0:
            start_time, elf = self.next_available_elf()

            time_left = self.hours.get_sanctioned_time_left(start_time)
            
            toy_idx = self.closest_toy_with_duration_idx(elf.rating * time_left * 1.01)
            toy_idx_exact = self.closest_toy_with_duration_idx(elf.rating * time_left * 1.0)
            
            if (  int(math.ceil(self.toys[toy_idx_exact].duration / elf.rating)) == time_left):
               toy_idx = toy_idx_exact-1
            
            if (  int(math.ceil(self.toys[toy_idx].duration / elf.rating)) > elf.rating * time_left*1.35   and (self.toys[toy_idx].duration ) < 5000):
               if (toy_idx >= 2):
                  toy_idx = toy_idx-1  # if we are too long for the time slot, cheat downwards
            
            
            size = 1
            target_rating = self.get_target(self.toys[len(self.toys) - 1].duration)

            if elf.rating > target_rating:
                toy_duration = self.toys[toy_idx + 1].duration / elf.rating
                if time_left > 580 and elf.rating > 3.99:
                    toy_idx = self.closest_toy_with_duration_idx(((time_left + 1440) * elf.rating))
                    toy = self.toys[toy_idx]
                    if elf.id == 1:
                        logging.info('Elf {0} eff {1} toy {2} duration {3} Big MEDIUM TOY[{4}]'.format(elf.id, elf.rating, toy.id, toy.duration, len(self.toys)))
                if toy_duration < (time_left * 1.2) and self.toys[toy_idx + 1].duration > (600 * target_rating):
                    toy_idx = toy_idx + 1
                    toy = self.toys[toy_idx]
                    if elf.id == 1:
                        logging.info('Elf {0} eff {1} toy {2} duration {3} MEDIUM2 TOY[{4}]'.format(elf.id, elf.rating, toy.id, toy.duration, len(self.toys)))
                elif (time_left < 60):
                     start_time = self.send_home_elf(elf)
                     if elf.id == 1:
                         logging.info('Elf {0} is going home early'.format(elf.id))
                     toy = None
                     continue
                else:
                    #Small optimization.  Look at all the leves that are about to finish and find where this elf's productivity is compared to the others.
                    #If its the 4th (for example) most productive elf then get the 4th biggest toy leaving the bigger toys to the other elves.
                    idx = self.get_elf_productivity_position(elf)
                    toy_idx = (idx + 1) * -1
                    toy = self.toys[ toy_idx]
                   # toy = self.toys.pop()
                    if elf.id == 1:
                       logging.info('Elf {0} eff {1} toy {2} duration {3} Big TOY[{4}] {5} {6}'.format(elf.id, elf.rating, toy.id, toy.duration, len(self.toys), elf.rating, toy_idx))
                    size=3
            elif self.toys[int(len(self.toys)/2)].duration > 400 and elf.rating > 0.25:
                toy_idx = -1
                toy = self.toys[-1]
                if elf.id == 1:
                    print 'Elf {0} eff {1} toy {2} duration {3} Big TOY[{4}] for balance'.format(elf.id, elf.rating, toy.id, toy.duration, len(self.toys))
            else:
                #if (elf.rating == 0.25 and self.toys[0].duration  > 69):
                #    toy_idx = len(self.toys) - 1
                toy = self.toys[toy_idx]
                if elf.id == 1:
                    logging.info('Elf {0} eff {1} toy {2} duration {3} SMALL TOY[{4}]'.format(elf.id, elf.rating, toy.id, toy.duration, len(self.toys)))
                size=1
            if (toy != None):
                productivity = elf.rating
                toy = self.toys.pop(toy_idx)
                elf, last_work_started, last_work_ended = self.record_work(elf, toy)
                solution.append({'elf_id':elf.id, 'toy_id':toy.id,'size':size, 'productivity': productivity, 'duration': toy.duration})
            self.return_elf(elf)

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


# input_file = sys.argv[1]
# output_file = sys.argv[2]
# num_elves = int(sys.argv[3])

# naive = SantasHelperSolutionNaive(input_file, output_file, num_elves)
# naive.process()
# #Disable postprocess. (Cause it doesnt work.)
# #reorder_solution()
# #post_process = SantasOrderedSolutionNaive(input_file, 'step2_' + output_file, num_elves)
# #post_process.process()


input_file = sys.argv[1]
output_file = sys.argv[2]
num_elves = int(sys.argv[3])

naive = SantasHelperSolutionNaive(input_file, output_file, num_elves)
naive.process()
#Disable postprocess. (Cause it doesnt work.)
#reorder_solution()
#post_process = SantasOrderedSolutionNaive(input_file, 'step2_' + output_file, num_elves)
#post_process.process()
