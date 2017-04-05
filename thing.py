### Q320: Spring 2012
### Cognitive Science Program, Indiana University
### Michael Gasser: gasser@cs.indiana.edu
###
### The things that populate the world, each with an associated Canvas object in the GUI.

from utils import *
from brain import *
from genome import *

## Things create their own Canvas object and record its id (different from self.id)

class Thing:

    RADIUS = 10
    """Radius of the Canvas object representing the thing."""

    N = 0
    """Number of things created."""

    color = 'red'
    """Color of the thing's Canvas object."""

    outline = 'white'
    """Outline color for Canvas object."""

    def __init__(self, world, coords):
        """Initialize location, food type, texture, solidity, id."""
        self.coords = coords
        self.world = world
        self.food = Thing
        self.id = Thing.N
        self.texture = 'empty'
        self.solid = True
        self.alive = False
        self.genome = None
        self.create_graphic()
        self.world.tag_bind(self.graphic_id, "<1>", self.describe)
        self.world.tag_bind(self.graphic_id, "<Double-1>", self.describe_verbosely)
        Thing.N += 1

    def __str__(self):
        """Print name for things."""
        return type(self).__name__ + str(self.id)

    def create_graphic(self):
        '''Create a graphic in the world for the Thing, and assign its id.'''
        x, y = self.coords
        self.graphic_id = self.world.create_oval(x - Thing.RADIUS, y - Thing.RADIUS,
                                                 x + Thing.RADIUS, y + Thing.RADIUS,
                                                 fill = self.color, outline = self.outline)

    def overlapping_same_type(self):
        '''Does the Thing overlap with another Thing of the same type?'''
        return self.world.overlapping_thing(self, type(self))

    def describe(self, event):
        '''Print out useful information about the Thing.'''
        print(self, '-- coordinates:', self.coords)

    def describe_verbosely(self, event):
        """Print out a lot of information about the Thing."""
        self.describe(event)

    def step(self):
        """Take primitive actions, if any, and update the thing."""
        pass

    def destroy(self):
        """Needed for some subclasses."""
        pass

class Clod(Thing):
    """A mineral."""

    color = 'blue'

    def __init__(self, world, coords):
        """Just for the texture."""
        Thing.__init__(self, world, coords)
        self.texture = 'hard'

class Fog(Thing):
    """Weather."""

    color = 'magenta'

    def __init__(self, world, coords):
        Thing.__init__(self, world, coords)
        self.solid = False

class Org(Thing):
    """A living thing."""

    INIT_STRENGTH = 300
    """Orgs start out with this strength."""

    MAX_STRENGTH = 600
    """Orgs can't get stronger than this."""

    LONGEVITY = 300
    """Number of steps an Org lives."""

    def __init__(self, world, coords):
        Thing.__init__(self, world, coords)
        self.strength = Org.INIT_STRENGTH
        self.max_strength = Org.MAX_STRENGTH
        self.longevity = Org.LONGEVITY
        self.alive = True
        # Number of time steps the org has been living
        self.age = 0

    def step(self):
        # Age by one
        Thing.step(self)
        self.age += 1
        if self.strength <= 0 or self.age >= self.longevity:
            self.die()

    def die(self):
        """The org is scheduled to be lost from the world."""
        self.alive = False

    def change_strength(self, amount):
        """Change the critter's strength by the amount (pos or neg)."""
        self.strength += amount
        self.strength = max([0, min([self.max_strength, self.strength])])

    def describe(self, event):
        '''Print out useful information about the Thing.'''
        Thing.describe(self, event)
        print('  strength:', self.strength)

    def describe_verbosely(self, event):
        """Print out lots of information about the Thing."""
        pass

class Plasmoid(Org):
    """A plant-like thing."""

    color = 'dark green'

    def __init__(self, world, coords):
        Org.__init__(self, world, coords)
        self.texture = 'soft'
        # Start with a random age so everything doesn't die at the same time
        self.age = random.randint(0, 200)

class Critter(Org):
    """An animate thing; it can move, turn, and take actions."""

    STEP_COST = 0
    """Amount a critter suffers just from living one time step."""

    HARD_BUMP_COST = -10
    """Amount a critter suffers when it collides with something hard."""

    SOFT_BUMP_COST = -2
    """Amount a critter suffers when it collides with something soft."""

    EAT_COST = -3
    """How much an attempt to eat costs."""

    MOVE_COST = -1
    """How much it costs to move."""

    TURN_COST = -1
    """How much it costs to turn."""

    MATE_COST = -200
    """How much it costs to mate."""

    MATE_PROB = .1
    """Governs likelihood of mating."""

    FOOD_REWARD = 50
    """Amount a critter gains when it eats food."""

    MOVE_DIST = 10
    """Distance critter moves."""

    BUMP_OFFSET = 0
    """How far into a clod a critter can go without actually colliding."""

    MOVE_PROB = .9
    """Probability of moving."""

    CHEW_RANGE = 8
    """Distance within which something can be chewed."""

    mouth_angle = 20
    """Opening of the critter's mouth."""

    def __init__(self, world, coords, heading=None):
        """Initialize strength and heading in addition to location."""
        self.heading = (heading if heading else random.randint(0, 360))
        Org.__init__(self, world, coords)
        self.move_dist = Critter.MOVE_DIST
        self.set_actions()
        self.set_sensor()
        self.set_brain()
        self.set_genome()

    def set_genome(self):
        '''Assign the critter's genome, if it has one.  Overridden in subclasses.'''
        self.genome = None

    def create_graphic(self):
        """Override create_graphic in Thing, to make a body with a mouth."""
        x, y = self.coords
        self.graphic_id = self.world.create_arc(x - Thing.RADIUS, y - Thing.RADIUS,
                                                x + Thing.RADIUS, y + Thing.RADIUS,
                                                # A little mouth
                                                start=self.heading + self.mouth_angle / 2,
                                                extent= 360 - self.mouth_angle,
                                                fill=self.color, outline=self.outline)

    def set_actions(self):
        """Set the critter's list of actions."""
        self.actions = [self.move, self.turn_right, self.turn_left, self.eat]
        
    def set_sensor(self):
        """Set the critter's sensor."""
        self.sensor = Sensor(self, self.world, [])

    def set_brain(self):
        """Set the critter's brain. By default the critter makes decisions randomly."""
        self.brain = Brain(self, self.sensor.get_n_state_features(), len(self.actions),
                           self.sensor, learning=False, genetic=False)

    def describe(self, event):
        '''Print out useful information about the Thing.'''
        Org.describe(self, event)
        sensed = self.sensor.sense()
        print('  sensed:', sensed)
        if self.brain.learning:
            print('  brain output:', self.brain.run(sensed))

    def describe_verbosely(self, event):
        """Print out lots of information about the Thing."""
        self.brain.show_weights()

    def destroy(self):
        '''Really get rid of the critter.'''
        self.sensor.destroy()

    def mouth_end(self):
        '''Coordinates of the point where the mouth opens.'''
        return get_endpoint(self.coords[0], self.coords[1], self.heading, Thing.RADIUS)

    def get_chewable(self):
        '''Things overlapping with the critter.'''
        end_x, end_y = self.mouth_end()
        return self.world.get_overlapping((end_x - Critter.CHEW_RANGE, end_y - Critter.CHEW_RANGE ,
                                           end_x + Critter.CHEW_RANGE, end_y + Critter.CHEW_RANGE),
                                          self.graphic_id)

    ## What the critter does on every time step
    
    def step(self):
        """Select an action, execute it, and receive the reinforcement."""
        # Mate with some probability with overlapping critters of the same species if your
        # brain is genetic
        if self.brain.genetic:
            overlap = self.overlapping_same_type()
            if overlap:
                # Mate with overlapping Thing?  But not till the end of the time step.
                if (overlap, self) not in self.world.to_mate and random.random() < self.mate_prob(overlap):
                    self.world.to_mate.append((self, overlap))
        # Sense
        new_state = self.sensor.sense()
        # Decide (for evolution, this just "asks" the genome)
        new_action = self.brain.decide(new_state)
        # Act and receive a reinforcement
        new_reinforcement = self.actions[new_action]()
        # Here is where learning happens in the Q-learning version
        if self.brain.learning:
            self.brain.learner.learn(new_state, new_action, new_reinforcement)
        # Change strength
        self.change_strength(new_reinforcement)
        # Age
        Org.step(self)

    ## Actions that can be selected

    def move(self):
        '''Move x and y in the direction of heading by move_dist unless a Clod is hit.'''
        x_dist, y_dist = xy_dist(self.heading, self.move_dist)
        x, y = self.world.adjust_coords(self.coords[0] + x_dist,
                                        self.coords[1] + y_dist)
        x1 = max(0, x - Thing.RADIUS + Critter.BUMP_OFFSET)
        y1 = max(0, y - Thing.RADIUS + Critter.BUMP_OFFSET)
        x2 = min(self.world.width, x + Thing.RADIUS - Critter.BUMP_OFFSET)
        y2 = min(self.world.height, y + Thing.RADIUS - Critter.BUMP_OFFSET)
        if self.world.overlaps_with(x1, y1, x2, y2,
                                    Clod):
            # Fail to move and get punished for the collision with the thing
            return Critter.HARD_BUMP_COST
        else:
            # Go ahead and move
            self.world.coords(self.graphic_id,
                              x - Thing.RADIUS, y - Thing.RADIUS,
                              x + Thing.RADIUS, y + Thing.RADIUS)
            self.coords = x, y
            self.sensor.move()
            return Critter.MOVE_COST

    def turn(self, angle=False):
        """Change the critter's heading by angle."""
        if not angle:
            self.heading = random.randint(0, 360)
        else:
            self.heading = (self.heading + angle) % 360
        self.world.itemconfigure(self.graphic_id,
                                 start = self.heading + self.mouth_angle / 2)
        self.sensor.turn()
        return Critter.TURN_COST

    def turn_left(self):
        '''Turn counterclockwise 50 degrees.'''
        return self.turn(50)

    def turn_right(self):
        '''Turn clockwise 50 degrees.'''
        return self.turn(310)

    def eat(self):
        '''Attempt to eat.'''
        cost = Critter.EAT_COST
        for c in self.get_chewable():
            if isinstance(c, self.food):
                cost += Critter.FOOD_REWARD
                c.die()
        return cost

    def mate(self):
        '''The critter mates with another.'''
        self.change_strength(Critter.MATE_COST)
        
    def mate_prob(self, potential):
        '''Probability of mating as a function of strength and potential mate's strength.'''
        return Critter.MATE_PROB * self.strength * potential.strength / (self.max_strength * self.max_strength)

class Diskoid(Critter):

    color = 'pink'

    def __init__(self, world, coords):
        """Diskoids are like other critters, except for their food and their sensor."""
        Critter.__init__(self, world, coords)
        self.food = Plasmoid
        self.texture = 'fuzzy'

    def set_sensor(self):
        """Make the Diskoid's sensor a set of feelers."""
        self.sensor = Feel(self, self.world,
                           # 1 short feeler at the mouth that can detect Plasmoids
                           [(0, 15)], ['soft'],
                           positional=True, genetic=True)

    def set_brain(self):
        """Set the Diskoid's brain (neural network)."""
        self.brain = Brain(self, self.sensor.get_n_state_features(), len(self.actions),
                           self.sensor, learning=False, genetic=True)

    def set_genome(self):
        '''Create the Diskoid's genome.'''
        self.genome = Genome(self, self.sensor.get_n_states(), len(self.actions))
        self.genome.initialize()

class Ringoid(Critter):
    """A type of critter that learns and doesn't evolve."""

    move_dist = 20

    color = 'black'
    outline = 'orange'

    def __init__(self, world, coords):
        """Ringoids are learners rather than evolver."""
        Critter.__init__(self, world, coords)
        self.food = Plasmoid
        # If you want Ringoids to move faster
#        self.move_dist = Ringoid.move_dist
        self.texture = 'fuzzy'
        self.strength = 500
        self.max_strength = 10000
        # They're immortal
        self.longevity = 1000000000

    def set_sensor(self):
        '''Feel sensor.'''
        self.sensor = Feel(self, self.world,
                           # 3 short feelers around mouth, one long one out of mouth
                           [(0, 13), (90, 13), (2, 20), (270, 13)],
                           ['hard', 'soft'],
                           positional=True)

    def set_brain(self):
        """Set the Ringoid's brain (neural network)."""
        self.brain = Brain(self, self.sensor.get_n_state_features(), len(self.actions),
                           self.sensor, learning=True, genetic=False)

class Sensor:

    def __init__(self, critter, world, features, symbolic=False, genetic=False):
        """Give the sensor a pointer to its critter."""
        self.critter = critter
        self.world = world
        self.features = features
        self.n_features = len(features)
        self.symbolic = symbolic
        self.genetic = genetic

    def get_n_states(self):
        """Number of different states."""
        return self.n_features

    def get_n_state_features(self):
        """Number of different state features."""
        return self.n_features

    def sense(self):
        """Get sensory information to be passed on to critter.

        If symbolic, return a list of strings.
        If genetic, return an int.
        """
        features = self.sense_symbolic()
        if self.symbolic:
            return features
        elif self.genetic:
            return self.symbolic2index(features)
        else:
            return self.symbolic2binary(features)

    def symbolic2index(self, symbolic):
        """Convert a list of strings to an int."""
        return 0

    def sense_symbolic(self):
        '''A list of features of things sensed.'''
        return [random.choice(self.features) for i in range(random.randint(0, 5))]

    def symbolic2binary(self, symbols):
        '''Converts a string of symbols to a list of binary numbers.'''
        return [1 if f in symbols else 0 for f in self.features]

    def move(self):
        '''Move the graphical object(s) for the Sensor.'''
        pass

    def turn(self):
        '''Turn the graphical object(s) for the Sensor.'''
        pass

    def destroy(self):
        '''Get rid of the graphical object(s).'''
        pass

class Feel(Sensor):
    '''One or more feelers that can sense textures at their ends.'''

    color = 'cyan'

    def __init__(self, critter, world, feeler_specs, textures,
                 positional=False, symbolic=False, genetic=False):
        '''Create the feelers, set features to be textures.

        If positional is true, there are separate texture sensors for
        different positions.'''
        Sensor.__init__(self, critter, world, textures, symbolic=symbolic, genetic=genetic)
        # Feelers is a list of angles and lengths for each feeler
        self.positional = positional
        self.feeler_specs = feeler_specs
        self.create_feelers()

    def get_n_states(self):
        """Number of different states, depending on positionality."""
        return (self.n_features + 1) ** len(self.feelers) if self.positional \
               else self.n_features + 1

    def get_n_state_features(self):
        """Number of different state features."""
        return (self.n_features + 1) * len(self.feelers) if self.positional \
               else self.n_features + 1

    def feeler_coords(self, angle, length):
        '''Coordinates of feeler with given angle and length.'''
        end_x, end_y = get_endpoint(self.critter.coords[0], self.critter.coords[1],
                                    (self.critter.heading + angle) % 360, length)
        return self.critter.coords[0], self.critter.coords[1], end_x, end_y

    def create_feelers(self):
        '''Create a Canvas object for each feeler, saving them in an attribute.'''
        self.feelers = [self.create_feeler(specs) for specs in self.feeler_specs]

    def create_feeler(self, angle_length):
        '''Create a Canvas object for an angle and length.'''
        coords = self.feeler_coords(*angle_length)
        if self.world:
            feeler_id = self.world.create_line(coords[0], coords[1], coords[2], coords[3],
                                               fill=self.color)
            self.world.tag_lower(feeler_id, self.critter.graphic_id)
        else:
            feeler_id = random.randint(1, 100)
        return feeler_id

    def sense_symbolic(self):
        '''List of Org textures felt by feelers; if positional, texture positions.'''
        found = []
        for index, feeler in enumerate(self.feelers):
            end_x, end_y = list(self.world.coords(feeler))[2:]
            new = [self.feature_label(t.texture, index) \
                   for t in self.world.get_point_overlapping(end_x, end_y, None) \
                   if t.texture in self.features]
            if new:
                if len(new) > 1:
                    # Pick just one feature per feeler
                    found.append(random.choice(new))
                else:
                    found.append(new[0])
            elif self.positional:
                found.append(self.feature_label('none', index))
        return found

    def feature_label(self, label, position):
        '''A label to add to a symbolic feature list.'''
        return label + str(position) if self.positional else label

    def symbolic2binary(self, symbols):
        '''Converts a string of symbols to a list of binary numbers.'''
        return reduce_lists([[1 if f in s else 0 for f in self.features + ['none']] for s in symbols])

    def symbolic2index(self, symbols):
        """Converts a string of symbols into an int."""
        nfeats = self.n_features + 1
        ext_feats = self.features + ['none']
        total = 0
        for index, symbol in enumerate(symbols):
            mult = nfeats ** index
            for pos, feat in enumerate(ext_feats):
                if feat in symbol:
                    total += pos * mult
        return total

    ## Methods to update the graphical objects
    
    def turn(self):
        '''Adjust graphics when critter turns.  Overrides method in Sense.'''
        for i, spec in zip(self.feelers, self.feeler_specs):
            coords = self.feeler_coords(*spec)
            self.world.coords(i, coords[0], coords[1], coords[2], coords[3])

    def move(self):
        '''Adjust graphics when critter moves.   Overrides method in Sense.'''
        for i, spec in zip(self.feelers, self.feeler_specs):
            coords = self.feeler_coords(*spec)
            self.world.coords(i, coords[0], coords[1], coords[2], coords[3])

    def destroy(self):
        '''Get rid of the graphical object(s).'''
        for f in self.feelers:
            self.world.delete(f)
