from tkinter import Tk, Canvas, PhotoImage, mainloop
from random import randint

def from_coolors(link: str) -> list[str]:
    # e.g. "https://coolors.co/8da1b9-95adb6-cbb3bf" -> ['#8da1b9', '#95adb6', '#cbb3bf'] 
    return list(map(lambda s: f"#{s}", link[link.rindex('/')+1::].split('-')))

def rgb_to_hex(r, g, b):
    return '#%02x%02x%02x' % (r,g,b)

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

WIDTH, HEIGHT = 1000, 1000

ant = Ant(WIDTH//2, HEIGHT//2) # star the ant in the center
rules = 'LRRRRRLLR' # the ruleset fort the game
colours = from_coolors("https://coolors.co/palette/001219-005f73-0a9396-94d2bd-e9d8a6-ee9b00-ca6702-bb3e03-ae2012-9b2226")

# init window
window = Tk()
canvas = Canvas(window, width=WIDTH, height=HEIGHT, bg=colours[0])
canvas.pack()
img = PhotoImage(width=WIDTH, height=HEIGHT)
canvas.create_image((WIDTH/2, HEIGHT/2), image=img, state="normal")

# fill the canvas with the first colour
for x in range(WIDTH):
    for y in range(HEIGHT):
        img.put(colours[0], (x,y))

try:
    while True:
        ant.move(img, rules, colours)
        window.update()
except:
    # when it goes off the screen stop
    mainloop()