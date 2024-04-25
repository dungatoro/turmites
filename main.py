# turn off 'Hello from the pygame community...' at start of script
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame

import cmd
import requests
import pickle

def from_lospec(palette):
    # get a palette from https://lospec.com/palette-list using their API
    try:
        response = requests.get(f"https://lospec.com/palette-list/{palette}.json")
    except:
        raise Exception
    else:
        return list(map(lambda s: f"#{s}".lower(), response.json()["colors"]))

def rgb_to_hex(r, g, b,a):
    return '#%02x%02x%02x' % (r,g,b)

def hex_to_rgb(hex):
    return tuple(int(hex[1::][i:i+2], 16) for i in (0, 2, 4))+(255,)

dirs = "NESW" # cardinal directions
class Ant:
    def __init__(self, x, y):
        self.pos = x, y
        self.dir = 'N' # starts facing north

    def turn_left(self):  
        self.dir = dirs[ dirs.index(self.dir)-1] # rotate the ant left

    def turn_right(self): 
        self.dir = dirs[(dirs.index(self.dir)+1)%4] # rotate the ant right

    def move(self, surface, rules, colours):
        colour = surface.get_at(self.pos) # get the colour at the canvas
        colour_idx = colours.index(colour) # find that colour in the palette

        # rotate the ant
        if rules[colour_idx] == 'R':
            self.turn_right()
        elif rules[colour_idx] == 'L':
            self.turn_left()

        # cycle the colour
        colour = colours[(colour_idx+1)%len(rules)] # colour palette wraps around
        surface.set_at(self.pos, colour) # write to the pixel

        # move the ant forward based on direction facing
        x, y = self.pos
        if   self.dir == 'N': self.pos = x,   y-1
        elif self.dir == 'E': self.pos = x+1, y
        elif self.dir == 'S': self.pos = x,   y+1
        elif self.dir == 'W': self.pos = x-1, y

class App(cmd.Cmd):
    width, height = 1000, 1000
    rules = "RL" # default langton's ant behaviour
    colours = ["#ffffff","#000000"]
    steps = 1000 # number of steps in the simulation at each frame
    sim_scale = 1 # scale the simulation by this factor
    sim_width, sim_height = width//sim_scale, height//sim_scale

    try:
        with open('turmites.pickle', 'rb') as f: # load any saved turmites
            turmites = pickle.load(f)
    except FileNotFoundError:
        turmites = {}

    prompt = " >> "

    def postcmd(self, stop, line):
        if len(self.rules) > len(self.colours): # warn about not enough colours
            print(f"WARNING: More rules than colours! There are currently {len(self.rules)} rules and only {len(self.colours)} colours.")

    def cmdloop(self, intro=None):
        print(intro)
        while True:
            try:
                super().cmdloop(intro="")
                break
            except KeyboardInterrupt: # handle CTRL+c to end the program
                print("^C")
                exit(0)

    def do_play(self, _):
        """ Start the simulation! 
    `play`"""
        ant = Ant(int(self.sim_width//2), int(self.sim_height//2)) # start the ant in the center

        colours = list(map(hex_to_rgb, self.colours)) # parse the colours to rgb form

        pygame.init()

        screen = pygame.display.set_mode((self.width, self.height))
        surface = pygame.Surface((self.sim_width, self.sim_height))
        surface.fill(colours[0]) # set the background to the first colour

        screen = pygame.display.get_surface()
        screen.blit(pygame.transform.scale_by(surface, self.sim_scale), (0,0))
        pygame.display.flip()

        try:
            while True:
                # need to listen for events otherwise OS will think the program has crashed
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        raise SystemExit

                # take `self.steps` steps in the simulation
                for i in range(self.steps):
                    ant.move(surface, self.rules, colours)

                screen.blit(pygame.transform.scale_by(surface, self.sim_scale), (0,0))
                pygame.display.flip()

        except:  # it will error when the ant tries to move outside the screen bounds
            # when it goes off the screen stop
            print("Ant has stopped.")
            # draw the screen as it wouldn't have drawn the last however many steps
            screen.blit(pygame.transform.scale_by(surface, self.sim_scale), (0,0))
            pygame.display.flip()

        # keep the window open until the user closes it or presses CTRL+c
        hold_window = True
        while hold_window:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    hold_window = False


    def do_new(self, line):
        """Quickly initialise a new simulation. 
    `new RLLRLRRLL 500 500`"""
        try:
            self.rules, width_str, height_str = line.split()
        except:
            print("Invalid number of arguments.")
        else:
            try:
                self.width, self.height = int(width_str), int(height_str)
            except ValueError:
                print("Width and height must be integers!")

    def do_set_rules(self, rules):
        """Define the rules for the simulation. 
    `set_rules RRLLLRLLLLLLLLL`"""
        rules = rules.upper()
        if set(rules) <= {'R', 'L'}:
            self.rules = rules.upper()
        else:
            print("Rules must only contains 'R's and 'L's")

    def do_set_size(self, line):
        """Set the WIDTHxHEIGHT of the screen. 
    `set_size 400x600`"""
        try:
            width_str, height_str = line.split('x')
        except:
            print("Invalid number of arguments.")
        else:
            try:
                self.width, self.height = int(width_str), int(height_str)
                self.sim_height, self.sim_width = self.height//self.sim_scale, self.width//self.sim_scale
            except ValueError:
                print("Width and height must be integers!")

    def do_set_scale(self, scale):
        """ Set the scale of the simulation.
    `set_scale 4`"""
        try:
            self.sim_scale = float(scale)
        except:
            print("Scale must be an float.")
        else:
            self.sim_height, self.sim_width = self.height//self.sim_scale, self.width//self.sim_scale
    
    def do_set_colours(self, colours):
        """Set the colours using a list of hex values.
    `set_colours 8da1b9 95adb6 cbb3bf`"""
        self.colours = list(map(lambda s: f"#{s}", colours.split()))

    def do_set_steps(self, steps):
        """Set the number of steps at each frame (more steps => faster). Using too many steps 
will make the simulation look choppy.
    `set_steps 1000`"""
        try:
            self.steps = int(steps)
        except:
            print("Must be an integer number of steps!")

    def do_from_lospec(self, palette):
        """Generate a colour palette from https://lospec.com/palette-list. Provide the 
palette name with '-' in place of spaces. 
    `from_lospec pico-8`"""
        try:
            self.colours = from_lospec(palette)
        except:
            print("Colour palette does not exist.")
    
    def do_list(self, _):
        """ List the saved turmites. 
    `list`"""
        for name in self.turmites:
            print(f' - "{name}"')

    def do_load(self, name):
        """ Load a previously saved turmite. This overwrites colours and rules. 
    `load scary fractal`"""
        try:
            turmite = self.turmites[name]
        except:
            print('No such turmite exists.')
        else:
            self.colours = turmite['colours']
            self.rules = turmite['rules'] 


    def do_save(self, name):
        """ Save the current colours and rules as a turmite to be loaded later! Please provide a name. 
    `save Streety's turmite`"""
        self.turmites[name] = {'colours': self.colours, 'rules': self.rules}
        with open('turmites.pickle', 'wb') as f:
            pickle.dump(self.turmites, f)

    def do_del(self, name):
        """ Delete an existing turmite by name.
    `del Williams' turmite`"""
        try:
            del self.turmites[name]
        except:
            print("Turmite does not exist.")
        else: 
            with open('turmites.pickle', 'wb') as f:
                pickle.dump(self.turmites, f)

intro = """
 __     ,  Welcome to Turmites!
(__).o.@c  Ask for `help` to see 
 /  |  \   a list of commands.
"""

App().cmdloop(intro)
