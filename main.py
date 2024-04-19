from tkinter import Tk, Canvas, PhotoImage, mainloop
import cmd
import requests
from PIL import Image

def from_coolors(link: str):
    # e.g. "https://coolors.co/8da1b9-95adb6-cbb3bf" -> ['#8da1b9', '#95adb6', '#cbb3bf'] 
    return list(map(lambda s: f"#{s}", link[link.rindex('/')+1::].split('-')))

def from_lospec(palette):
    response = requests.get(f"https://lospec.com/palette-list/{palette}.json")
    return list(map(lambda s: f"#{s}".lower(), response.json()["colors"]))

def rgb_to_hex(r, g, b):
    return '#%02x%02x%02x' % (r,g,b)

def hex_to_rgb(hex):
    return tuple(int(hex[1::][i:i+2], 16) for i in (0, 2, 4))

dirs = "NESW" # cardinal directions
class Ant:
    def __init__(self, x, y):
        self.pos = x, y
        self.dir = 'N' # starts facing north

    def turn_left(self):  
        self.dir = dirs[ dirs.index(self.dir)-1] # rotate the ant left

    def turn_right(self): 
        self.dir = dirs[(dirs.index(self.dir)+1)%4] # rotate the ant right

    def move(self, img, rules, colours):
        colour = rgb_to_hex(*img.get(*self.pos)) # get the colour at the canvas
        colour_idx = colours.index(colour) # find that colour in the paletter

        # rotate the ant
        if rules[colour_idx] == 'R':
            self.turn_right()
        elif rules[colour_idx] == 'L':
            self.turn_left()

        # cycle the colour
        colour = colours[(colour_idx+1)%len(rules)] # colour palette wraps around
        img.put(colour, self.pos)

        # move the ant forward
        x, y = self.pos
        if   self.dir == 'N': self.pos = x,   y-1
        elif self.dir == 'E': self.pos = x+1, y
        elif self.dir == 'S': self.pos = x,   y+1
        elif self.dir == 'W': self.pos = x-1, y

class App(cmd.Cmd):
    rules = "RRLLLRLLLLLLLLL" # default ruleset
    # default 16 colour palette
    colours = ["#1a1c2c","#5d275d","#b13e53","#ef7d57","#ffcd75","#a7f070","#38b764",
               "#257179","#29366f","#3b5dc9","#41a6f6","#73eff7","#f4f4f4","#94b0c2",
               "#566c86","#333c57"] 
    width, height = 500, 500
    prompt = " >> "

    def postcmd(self, stop, line):
        if len(self.rules) > len(self.colours):
            print(f"\033[93mWARNING: More rules than colours!\033[0m There are currently {len(self.rules)} rules and {len(self.colours)} colours.")

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
        """ Quickly initialise a new simulation e.g. `new RLLRLRRLL 500 500` """
        try:
            self.rules, width_str, height_str = line.split()
        except:
            print("Invalid number of arguements")

        try:
            self.width, self.height = int(width_str), int(height_str)
        except ValueError:
            print("Width and height must be integers!")

    def do_set_rules(self, rules):
        """ Define the rules for the simulation. e.g. RRLLLRLLLLLLLLL """
        self.rules = rules

    def do_set_width(self, width):
        """ Set the width of the screen in pixels. """
        try:
            self.width = int(width)
        except ValueError:
            print("Width must be an integer!")

    def do_set_height(self, width):
        """ Set the height of the screen in pixels. """
        try:
            self.height = int(width)
        except ValueError:
            print("Height must be an integer!")
    
    def do_set_colours(self, colours):
        """ Set the colours using a list of hex values. e.g. 8da1b9 95adb6 cbb3bf. """
        self.colours = list(map(lambda s: f"#{s}", colours.split()))

    def do_from_coolors(self, link):
        """ Another way to set the colours. Generate a colour palette from a https://coolors.co link. """
        self.colours = from_coolors(link)

    def do_from_lospec(self, palette):
        """ Yet another way to set the colours. Generate a colour palette from a palette name on lospec. """
        self.colours = from_lospec(palette)

    def do_play(self, _):
        """ 
        Start the simulation!
        """
        ant = Ant(self.width//2, self.height//2) # start the ant in the center

        window = Tk()
        canvas = Canvas(window, width=self.width, height=self.height) # create the blank window
        canvas.pack()

        i = Image.new('RGB', (self.width, self.height), hex_to_rgb(self.colours[0])) # generate a single colour image
        i.save('t_u_r_m_i_t_e.png')
        img = PhotoImage(file='t_u_r_m_i_t_e.png') # open the image as a `PhotoImage`, for pixel manipulation

        canvas.create_image((self.width/2, self.height/2), image=img)

        try:
            while True:
                ant.move(img, self.rules, self.colours)
                window.update()
        except: 
            # when it goes off the screen stop
            print("Ant has stopped.")
            mainloop()

intro = """
 __     ,  Welcome to Turmites!
(__).o.@c  Ask for `help` to see 
 /  |  \   a list of commands.
"""

App().cmdloop(intro)