import cmd
import requests
import pickle
import pygame

def from_lospec(palette):
    response = requests.get(f"https://lospec.com/palette-list/{palette}.json")
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
        surface.set_at(self.pos, colour)

        # move the ant forward
        x, y = self.pos
        if   self.dir == 'N': self.pos = x,   y-1
        elif self.dir == 'E': self.pos = x+1, y
        elif self.dir == 'S': self.pos = x,   y+1
        elif self.dir == 'W': self.pos = x-1, y

class App(cmd.Cmd):
    width, height = 1000, 1000
    rules = "RL"
    colours = ["#ffffff","#000000"]
    steps = 1000

    with open('turmites.pickle', 'rb') as f:
        turmites = pickle.load(f)

    prompt = " >> "

    def postcmd(self, stop, line):

        if len(self.rules) > len(self.colours): # warn about not enough colours
            print(f"WARNING: More rules than colours! There are currently {len(self.rules)} rules and {len(self.colours)} colours.")

    def cmdloop(self, intro=None):
        print(intro)
        while True:
            try:
                super().cmdloop(intro="")
                break
            except KeyboardInterrupt:
                print("^C")
                exit(0)

    def do_new(self, line):
        """ Quickly initialise a new simulation e.g. `new RLLRLRRLL 500 500`. """
        try:
            self.rules, width_str, height_str = line.split()
        except:
            print("Invalid number of arguments.")

        try:
            self.width, self.height = int(width_str), int(height_str)
        except ValueError:
            print("Width and height must be integers!")

    def do_set_rules(self, rules):
        """ Define the rules for the simulation. e.g. RRLLLRLLLLLLLLL. """
        rules = rules.upper()
        if set(rules) <= {'R', 'L'}:
            self.rules = rules.upper()
        else:
            print("Rules must only contains 'R's and 'L's")

    def do_set_size(self, line):
        """ Set the WIDTHxHEIGHT of the screen. """
        try:
            width_str, height_str = line.split('x')
        except:
            print("Invalid number of arguments.")

        try:
            self.width, self.height = int(width_str), int(height_str)
        except ValueError:
            print("Width and height must be integers!")
    
    def do_set_colours(self, colours):
        """ Set the colours using a list of hex values. e.g. 8da1b9 95adb6 cbb3bf. """
        self.colours = list(map(lambda s: f"#{s}", colours.split()))

    def do_set_steps(self, steps):
        """ Set the number of steps at each frame (more steps => faster). """
        try:
            self.steps = int(steps)
        except:
            print("Must be an integer number of steps!")

    def do_from_lospec(self, palette):
        """ Generate a colour palette from a palette name on lospec. """
        self.colours = from_lospec(palette)
    
    def do_play(self, _):
        """ Start the simulation! """
        ant = Ant(self.width//2, self.height//2) # start the ant in the center

        colours = list(map(hex_to_rgb, self.colours))

        pygame.init()

        screen = pygame.display.set_mode((self.width, self.height))
        surface = pygame.Surface((self.width, self.height))
        surface.fill(colours[0])

        screen = pygame.display.get_surface()
        screen.blit(surface, (0,0))
        pygame.display.flip()

        try:
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        raise SystemExit

                for i in range(self.steps):
                    ant.move(surface, self.rules, colours)
                screen.blit(surface, (0,0))
                pygame.display.flip()
        except: 
            # when it goes off the screen stop
            print("Ant has stopped.")
            screen.blit(surface, (0,0))
            pygame.display.flip()

        hold_window = True
        while hold_window:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    hold_window = False

    def do_list(self, _):
        """ List the saved turmites. """
        for name in self.turmites:
            print(f' - "{name}"')

    def do_load(self, name):
        """ Load a previously saved turmite. This overwrites colours and rules. """
        try:
            turmite = self.turmites[name]
        except:
            print('No such turmite exists.')
        else:
            self.colours = turmite['colours']
            self.rules = turmite['rules'] 

    def do_save(self, name):
        """ Save the current colours and rules as a turmite to be loaded later! Please provide a name. """
        self.turmites[name] = {'colours': self.colours, 'rules': self.rules}
        with open('turmites.pickle', 'wb') as f:
            pickle.dump(self.turmites, f)

intro = """
 __     ,  Welcome to Turmites!
(__).o.@c  Ask for `help` to see 
 /  |  \   a list of commands.
"""

App().cmdloop(intro)