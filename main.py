#!/usr/bin/env python3

### Q320: Spring 2012
### Cognitive Science Program, Indiana University
### Michael Gasser: gasser@cs.indiana.edu
###
### Evolution World
### A toroidal world with diskoids that can move around in it
### and plasmoids that just sit there. The diskoids can evolve
### to respond to the feedback they receive.
### There are also classes (in brain.py) for Q learning using
### lookup tables or neural networks.

from tkinter import *
from thing import *

# Delay in microseconds between steps during Run
STEP_DELAY = 0

class WorldFrame(Frame):
    '''A Frame in which to display the world.'''

    def __init__(self, root, width=450, height=450):
        '''Give the frame a canvas and display it.'''
        Frame.__init__(self, root)
        self.world = World(self, width=width, height=height)
        root.title('The World')
        step_button = Button(self, text='Step')
        step_button.grid(row=1, column=0)
        step_button.bind('<1>', self.world.step)
        run_button = Button(self, text='Run')
        run_button.grid(row=1, column=1)
        run_button.bind('<1>', self.world.run)
        self.evolve_button = Button(self, text='Adapt')
        self.evolve_button.bind('<Button-1>', self.world.adapt)
        self.evolve_button.grid(row=1, column=2)
        self.grid()

class World(Canvas):
    """The arena where everything happens."""

    COLOR = 'black'
    """Color for the Canvas background."""
    EDGE = 2
    """Along each border leave this much free."""
    STEPS_PER_RUN = 500
    """Number of steps to run when the 'Run' button is pushed."""

    THINGS = {# Diskoid: {'init': 30, 'min': 0, 'max': 50},
              Ringoid: {'init': 5, 'min': 0, 'max': 50},
              Plasmoid: {'init': 75, 'min': 75, 'max': 80}}

    def __init__(self, frame, width=450, height=450):
        """Initialize dimensions and create things."""
        Canvas.__init__(self, frame, bg = World.COLOR,
                        width=width, height=height)
        self.frame = frame
        self.width = width
        self.height = height
        # Dict of things, indexed by their canvas object ids
        self.things = {}
        for tp, dct in World.THINGS.items():
            for i in range(dct['init']):
                self.add_thing(tp)
        # Things to mate on a given time step
        self.to_mate = []
        self.grid(row=0, columnspan=3)
        # Number of time steps elapsed so far
        self.steps = 0

    def adapt(self, event):
        """Handler for the Evolve button.
        Binds the button to the other handler."""
        print('Starting evolution and learning')
        Genome.evolve = True
        Network.eta = 0.05
        self.frame.evolve_button.config(text="Don't adapt")
        self.frame.evolve_button.bind('<Button-1>', self.dont_adapt)

    def dont_adapt(self, event):
        """Handler for the Evolve button.
        Binds the button to the other handler."""
        print('Turning off evolution and learning')
        Genome.evolve = False
        Network.eta = 0.0
        self.frame.evolve_button.config(text="Adapt")
        self.frame.evolve_button.bind('<Button-1>', self.adapt)

    def add_thing(self, tp):
        '''Create a thing of a given type and index.'''
        coords = self.get_thing_coords()
        thing = tp(self, coords)
        self.things[thing.graphic_id] = thing
        return thing

    def get_thing_coords(self):
        '''Coordinates for a new thing.'''
        x, y = (random.randint(Thing.RADIUS + World.EDGE,
                               self.width - Thing.RADIUS - World.EDGE),
                random.randint(Thing.RADIUS + World.EDGE,
                               self.height - Thing.RADIUS - World.EDGE))
        if self.overlaps_with(x - Thing.RADIUS, y - Thing.RADIUS,
                              x + Thing.RADIUS, y + Thing.RADIUS,
                              Clod):
            return self.get_thing_coords()
        else:
            return x, y

    def get_overlapping(self, coords, except_thing):
        '''Things that overlap with coordinates coords other than except_thing.'''
        return [self.things[thing_id] for thing_id in \
                self.find_overlapping(coords[0], coords[1], coords[2], coords[3]) \
                if thing_id in self.things and thing_id != except_thing]

    def overlaps_with(self, x1, y1, x2, y2, kind, exclude=-1):
        '''Does the region with coordinates x1, y1, x2, y2 overlap with any of type kind?'''
        return some(lambda x: isinstance(self.things.get(x, None), kind) and x != exclude,
                    self.find_overlapping(x1, y1, x2, y2))

    def thing_overlaps_with(self, x, y, kind):
        '''Does the Thing overlap with any of type kind?'''
        return some(lambda x: isinstance(self.things.get(x, None), kind),
                    self.find_overlapping(x - Thing.RADIUS, y - Thing.RADIUS,
                                          x + Thing.RADIUS, y + Thing.RADIUS))

    def get_point_overlapping(self, x, y, except_thing):
        '''Things that overlap with a tiny square around x,y.'''
        return self.get_overlapping((x - 1, y - 1, x + 1, y + 1), except_thing)

    def overlapping_thing(self, thing, kind):
        '''First Thing of type kind that overlaps with thing.'''
        x, y = thing.coords
        for i in self.find_overlapping(x - Thing.RADIUS, y - Thing.RADIUS,
                                       x + Thing.RADIUS, y + Thing.RADIUS):
            if i != thing.graphic_id:
                thing2 = self.things.get(i, None)
                if isinstance(thing2, kind):
                    return thing2

    def adjust_coords(self, x, y):
        '''Adjust coordinates of moved Critter assuming the world wraps around.'''
        if x < 0:
            x = self.width + x
        elif x > self.width:
            x = x - self.width
        if y < 0:
            y = self.height + y
        elif y > self.height:
            y = y - self.height
        return x, y

    def n_things(self, typ):
        '''Number of things in the world of a given type.'''
        return len([thing for thing in self.things.values() if isinstance(thing, typ)])

    def step(self, event):
        """Step each of the things and update the number of things if necessary."""
        # Create new things if necessary
        for tp, dct in World.THINGS.items():
            mn = dct['min']
            n = self.n_things(tp)
            if n < mn:
                for x in range(mn - n):
                    self.add_thing(tp)
        # Now do the actual stepping
        for thing in self.things.values():
            thing.step()
        # Kill off the things that are supposed to die
        to_die = []
        for thing in list(self.things.values()):
            if isinstance(thing, Org) and not thing.alive:
                del self.things[thing.graphic_id]
                self.delete(thing.graphic_id)
                thing.destroy()
        # Mate the pairs selected to mate
        for parent1, parent2 in self.to_mate:
            self.mate(parent1, parent2)
        self.to_mate = []
        self.steps += 1

    def mate(self, parent1, parent2):
        '''Produce two offspring from parents and add them to the world.'''
        typ = type(parent1)
        typ_max = World.THINGS[typ].get('max')
        if typ_max and self.n_things(typ) < typ_max - 1:
            # Only allow mating if we won't go over the max for this type
            offspring1 = self.add_thing(typ)
            offspring2 = self.add_thing(typ)
            parent1.mate()
            parent2.mate()
            if parent1.genome and parent2.genome:
                parent1.genome.crossover(parent2.genome, offspring1, offspring2)

    def run(self, event):
        """Run step() 'steps' times on everything, and print the world."""
        for s in range(World.STEPS_PER_RUN):
            # Wait for STEP_DELAY microseconds
            self.after(STEP_DELAY)
            self.step(event)
            self.update_idletasks()
        self.show_stats()

    def show_stats(self):
        '''Print useful statistics about the types in the population of orgs.'''
        print('POPULATION AFTER', self.steps, 'STEPS')
        for t_type, t in World.THINGS.items():
            if issubclass(t_type, Org):
                strength_sum = 0.0
                n = 0
                max_s = 0
                for t1 in [t2 for t2 in self.things.values() if isinstance(t2, t_type)]:
                    strength = t1.strength
                    strength_sum += strength
                    if strength > max_s:
                        max_s = strength
                    n += 1
                if n != 0:
                    print(t_type.__name__ + ':  N', n, ' mean strength',
                          int(strength_sum / n), ' max strength', max_s)
        # Uncomment the following if you want to show all the genomes
#        for t in self.things.values():
#            if t.genome:
#                t.genome.show()

root = Tk()
frame = WorldFrame(root)
root.mainloop()
