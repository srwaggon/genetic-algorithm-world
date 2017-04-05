### Q320: Spring 2012
### Cognitive Science Program, Indiana University
### Michael Gasser: gasser@cs.indiana.edu
###
### Genomes specifying actions given particular states.

from utils import *

class Genome(list):
    '''Class for genomes, which are lists of values.'''

    evolve = False

    MUTATION = .005
    """Mutation rate"""
    CROSSOVER = .7
    """Probability of crossover"""
    BITS_PER_VALUE = 3
    """Number of bits used for each 'q-value'"""

    def __init__(self, animal, n_states, n_actions):
        self.animal = animal
        self.n_states = n_states
        self.n_actions = n_actions
        self.length = n_actions * n_states * Genome.BITS_PER_VALUE

    def initialize(self):
        '''Set the length and random bits in the genome.'''
        for a in range(self.length):
            self.append(random.random() < .5)

    def copy(self, animal):
        '''Make a copy of this Genome, but for a different animal. If Genome.evolve
        is False, just copy the number of bits, not the actual values.'''
        g = Genome(animal, self.n_states, self.n_actions)
        if Genome.evolve:
            for a in range(g.length):
                g.append(self[a])
            return g
        g.initialize()
        return g

    def mutate(self):
        '''With probability MUTATION, flip the bits in the Genome.'''
        for a in range(len(self)):
            if random.random() < Genome.MUTATION:
                self[a] = not self[a]

    def crossover(self, mate_genome, offspring1, offspring2):
        '''Perform crossover between this genome and mate_genome,
        given the two offspring already.'''
        # Make the genomes of the offspring copies of self and mate_genome
        genome1 = self.copy(offspring1)
        genome2 = mate_genome.copy(offspring2)
        offspring1.genome = genome1
        offspring2.genome = genome2
        if random.random() < Genome.CROSSOVER:
            # Swap everything up to the crossover point
            crossover_point = random.randint(1, self.length - 1)
            genome1[:crossover_point] = mate_genome[:crossover_point]
            genome2[:crossover_point] = self[:crossover_point]
        # Mutate the crossed-over genomes
        genome1.mutate()
        genome2.mutate()

    def get_groups(self):
        '''Sublists representing q-values.'''
        return [self[start:start+Genome.BITS_PER_VALUE] for start in range(0, self.length, Genome.BITS_PER_VALUE)]

    def get_values(self):
        '''List of values represented by genome.'''
        return [self.to_value(ls) for ls in self.get_groups()]

    def get_state_values(self, state_index):
        '''List of values for state with index state_index.'''
        start = state_index * self.n_actions
        return self.get_values()[start:(start + self.n_actions)]

    def get_best_action(self, state_index):
        '''Return the index of the best action for the given state.'''
        state_values = self.get_state_values(state_index)
        highest = max(state_values)
        return state_values.index(max(state_values))

    def get_value(self, state_index, action_index):
        '''Value for state-action pair.'''
        return self.get_state_values(state_index)[action_index]

    def to_value(self, sublist):
        '''Convert the sublist (length BITS_PER_VALUE) to a "q-value".'''
        return bin_to_dec(sublist)

    def show(self):
        '''Print out the bits in the genome.'''
        for v in self.get_values():
            print(v, end=' ')
        print()
##        s = ''
##        for i,a in enumerate(self):
##            if i % BITS_PER_WEIGHT == 0 and i != 0:
##                s += '|'
##            s += ('1' if a else '0')
##        print s
            

