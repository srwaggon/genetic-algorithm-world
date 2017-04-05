### Q320: Spring 2012
### Cognitive Science Program, Indiana University
### Michael Gasser: gasser@cs.indiana.edu
###
### Feedforward neural network with some number of layers that implement
### Q learning.
### Brain, a subclass of Network, but only actually implements the network
### if its learning attribute is True. It's responsible for deciding; how
### that works depends on whether the brain is a 'learning' or 'genetic' brain.

from utils import *

## RANDOM WEIGHT AND ACTIVATION GENERATION

def random_act(min_act, max_act):
    '''Generate a random activation between min_act and max_act.'''
    return min_act + random.random() * (max_act - min_act)

def random_weight(wt_range, neg=True):
    '''Generate a random weight within wt_range. If neg is True, value may be negative.'''
    val = random.random() * wt_range
    if neg:
        val = val - wt_range / 2
    return val

class Network:
    '''A feedforward neural network with an ordered set of Layers of units.'''

    eta = 0.0
    """Learning rate."""

    def __init__(self, name, layers):
        '''Initialize, creating input, hidden, and output Layers and weights.'''
        self.name = name
        # List of layers in input - hidden - output order
        self.layers = layers
        self.initialize()

    def __str__(self):
        '''Print name for the Network.'''
        return self.name

    def initialize(self):
        '''Initialize the Layers, including weights to output Layers.'''
        for i in range(1, len(self.layers)):
            # Default connectivity: each layer feeds into the next
            self.layers[i].input_layer = self.layers[i-1]
            self.layers[i-1].output_layer = self.layers[i]
        # Now create the weights
        for l in self.layers:
            l.initialize()

    def reinit(self):
        '''Reinitialize: all Layers but the input Layer.'''
        for l in self.layers[1:]:
            l.initialize_weights()

    def propagate_forward(self):
        '''Propagate activation forward through the network.'''
        for l in self.layers[1:]:
            l.update()

    def run(self, pattern, target=[]):
        '''Run the network on one pattern, returning the output pattern.'''
        # Clamp the input Layer to the pattern (a list or tuple).
        # Fail if the pattern is the wrong length
        error = 0
        if self.layers[0].clamp(pattern):
            # Update the other Layers in sequence
            self.propagate_forward()
            # Train
            if target:
                error = self.layers[-1].do_errors(target)
                self.propagate_backward()
                self.update_weights()
            return self.layers[-1].activations

    def propagate_backward(self):
        '''Propagate error backward through the network.'''
        for l in reversed(self.layers[1:-1]):
            l.update_error()

    def update_weights(self):
        """Update the weights in reverse order."""
        for l in reversed(self.layers[1:]):
            l.learn()

    def show_activations(self):
        '''Print input pattern and output activation.'''
        for l in self.layers:
            l.show_activations()

    def show_weights(self):
        '''Print the weights and biases in the newtork.'''
        for l in self.layers[1:]:
            l.show_weights()

class Layer:
    '''A list of units, each with an activation.'''

    def __init__(self, name, size=10, weight_range=.5, linear=False):
        '''Initialize variables, but not the list of activations or weights.'''
        self.size = size
        # Layer feeding this lLayer
        self.input_layer = None
        # Layer this Layer feeds
        self.output_layer = None
        # Whether the activation function is the identity function
        self.linear=linear
        self.weights = []
        self.name = name
        self.min_activation = 0.0
        self.max_activation = 1.0
        self.activations = self.gen_random_acts()
        self.errors = [0.0 for u in range(self.size)]
        self.weight_range = weight_range

    def __str__(self):
        '''Print name for Layer.'''
        return self.name

    def initialize(self):
        '''Create the activations and weights lists.'''
        if self.input_layer:
            # This has an input_layer, so it has weights into it
            self.initialize_weights()

    def initialize_weights(self):
        '''Create the weights list of lists and a bias for each unit.

        Indices: [dest-index][input-unit-index]
        Bias is the last value in each weight list (index self.input_layer.size)
        '''
        self.weights = [ [random_weight(self.weight_range) for i in range(self.input_layer.size)] \
                         # Bias weight
                         + [random_weight(self.weight_range)] \
                         for u in range(self.size)]

    def gen_random_acts(self):
        '''Generate random activations.'''
        return [random_act(self.min_activation, self.max_activation) for u in range(self.size)]

    def clamp(self, v):
        '''Clamp pattern vector v on this Layer.'''
        if len(v) != self.size:
            print('Vector', v, 'is the wrong size')
        else:
            for i in range(self.size):
                self.activations[i] = v[i]
            return True

    def get_input(self, dest_i):
        '''Get input into unit dest_i, including [1.0] for bias.'''
        return dot_product(self.input_layer.activations + [1.0], self.weights[dest_i])

    def update(self):
        '''Update unit activations.'''
        for index in range(self.size):
            inp = self.get_input(index)
            self.activations[index] = inp if self.linear else sigmoid(inp, 0.0, 1.0)

    def do_errors(self, target):
        '''Figure the errors for each (output) unit, given the target pattern, returning RMS error.'''
        error = 0.0
        for i in range(self.size):
            target_i = target[i]
            if isinstance(target_i, str):
                # Indicates there should be no learning into this output unit
                self.errors[i] = 0.0
            else:
                e = target_i - self.activations[i]
                self.errors[i] = e
                error += e * e
        return math.sqrt(error / self.size)

    def learn(self):
        '''Update the weights into the layer.'''
        for u in range(self.size):
            error = self.errors[u]
            act_slope = 1.0 if self.linear else sigmoid_slope(self.activations[u])
            for i in range(self.input_layer.size):
                self.weights[u][i] += error * Network.eta * act_slope * self.input_layer.activations[i]
            # Bias weight
            self.weights[u][self.input_layer.size] += Network.eta * error * act_slope

    def show_activations(self):
        '''Print activations.'''
        print(self.name.ljust(12), end=' ')
        for a in self.activations:
            print('%.3f' % a, end=' ')
        print()

    def show_weights(self):
        '''Print the weights and biases in the layer.'''
        print(self.name)
        for u in range(self.size):
            print(str(u).ljust(5), end=' ')
            for w in range(len(self.weights[u])):
                print('%+.3f' % self.weights[u][w], end=' ')
            print()

class Brain(Network):
    """A brain that is a neural network."""

    exploitation = 1.0
    """Parameter controlling exploration-exploitation tradeoff."""

    def __init__(self, animal, n_senses, n_actions,
                 sensor, genetic=True, learning=False):
        """The brain needs to know the number of sense features (inputs) and actions (outputs)."""
        if learning:
            # Only actually create the neural network if learning is True
            Network.__init__(self, animal.__str__() + '_brain',
                             [Layer('sense_in', n_senses),
                              Layer('act_out', n_actions, weight_range=0.0, linear=True)])
        self.animal = animal
        self.n_actions = n_actions
        self.n_senses = n_senses
        self.genetic = genetic
        self.learning = learning
        if learning:
            # Create the learner only if learning is True
            self.learner = QLearner(self)

    def decide(self, state):
        '''Decide what to do by choosing an action index.'''
        if self.learning:
            # Uses q values in the learning version
            return exp_luce_choice(self.get_Qs(state), Brain.exploitation)
        elif self.genetic:
            # Let the genome decide
            return self.animal.genome.get_best_action(state)
        else:
            # Randomly choose an action index
            return random.randint(0, self.n_actions - 1)

    def get_Qs(self, state, run=True):
        """The Q values for a given state input.
        If run=False, the network doesn't need to be run first."""
        if run:
            return self.run(state)
        else:
            return self.layers[-1].activations

class QLearner:
    """Learn Q values in a neural network."""

    gamma = .8
    """Discount rate for Q learning."""

    def __init__(self, brain):
        """Initialize the 3 things that need to be remembered from the previous time step."""
        self.brain = brain
        self.last_reinforcement = 0
        self.last_state = None
        self.last_action = None

    def newQ(self):
        """Assumes the brain network has just been run in the 'next' state."""
        return self.last_reinforcement + QLearner.gamma * self.get_best_Q()

    def get_best_Q(self):
        """The highest value on the output layer of the network."""
        return max(self.brain.layers[-1].activations)

    def make_target(self):
        """A list representing the target for learning about the last time step."""
        return [('x' if i != self.last_action else self.newQ()) for i in range(self.brain.layers[-1].size)]

    def learn(self, new_state, new_action, new_reinforcement):
        """Run the network with the last state as input and update the weights into the last action unit."""
        # Don't learn if this is the first time step of learning
        if self.last_state:
            self.brain.run(self.last_state, self.make_target())
        # Update the stored values for learning on the next time step
        self.last_reinforcement = new_reinforcement
        self.last_state = new_state
        self.last_action = new_action
