import sys
import random

from SantasHelperSolution import *

class SantasHelperSolutionGeneration:
    def __init__(self, toy_filename, output_filename, population_size, total_elves = NUM_ELVES):
        self.population_size = population_size + population_size % 2
        self.genes = [SantasHelperSolutionGenetic(toy_filename, output_filename, total_elves) for i in xrange(self.population_size)]
        self._next_gene_id = 0
        for i in xrange(len(self.genes)):
            self.genes[i].init_gene(self, self.next_gene_id())

    def run(self, generations = 1):
        for x in xrange(generations):
            print "Running Generation #%d" % (x + 1)

            for i in xrange(len(self.genes)):
                self.genes[i].process()
                print "... [%d] processed gene %d/%d with fitness: %d" % (x + 1, i, self.population_size, self.genes[i].fitness())

            self.genes = sorted(self.genes, key = lambda g: g.fitness())

            new_genes = []
            for i in xrange(0, len(self.genes), 2):
                c1, c2 = self.genes[i].mate_with(self.genes[i + 1])
                new_genes.append(c1)
                new_genes.append(c2)
            self.genes = new_genes

    def next_gene_id(self):
        self._next_gene_id = self._next_gene_id + 1
        return self._next_gene_id


class SantasHelperSolutionGenetic(SantasHelperSolution):
    def init_gene(self, generation, gene_id, gene = None):
        self.generation = generation
        self.gene_id = gene_id
        self.output_filename = string.replace(self.output_filename, '.', "_gene_%s." % (gene_id))
        if gene is None:
            self._init_random_gene()
        else:
            self._gene = gene

    def _init_random_gene(self):
        self._gene = [toy for toy in self.toys]
        random.shuffle(self._gene)

    def run(self):
        self.last_work_started  = None
        self.last_work_ended    = None

        for toy in self._gene:
            start_time, elf = self.next_available_elf()
            self.last_work_started, self.last_work_ended = self.record_work(elf, toy)

    def fitness(self):
        return int((self.last_work_ended - self.base_time).total_seconds())

    def mate_with(self, other_gene):
        crossover_points = random.randint(1, 5)
        g1 = g2 = None
        for crossover in xrange(crossover_points):
            point = random.randint(1, len(self._gene) - 1)
            if g1 is None:
                g1 = self._gene[0:point] + other_gene._gene[point:len(self._gene)]
                g2 = other_gene._gene[0:point] + self._gene[point:len(self._gene)]
            else:
                g1 = g1[0:point] + g2[point:len(self._gene)]
                g2 = g2[0:point] + g1[point:len(self._gene)]
        child1 = SantasHelperSolutionGenetic(self.toy_filename, self.output_filename, self.total_elves)
        child2 = SantasHelperSolutionGenetic(self.toy_filename, self.output_filename, self.total_elves)

        child1.init_gene(self.generation.next_gene_id(), g1)
        child2.init_gene(self.generation.next_gene_id(), g2)

        return child1, child2

input_file = sys.argv[1]
output_file = sys.argv[2]
num_elves = int(sys.argv[3])
population_size = int(sys.argv[4])
generations = int(sys.argv[5])

solution = SantasHelperSolutionGeneration(input_file, output_file, population_size, num_elves)
solution.run(generations)
