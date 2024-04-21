```
 __     ,  
(__).o.@c  Welcome to Turmites!
 /  |  \ 
```

A python simulation of [Lanton's ant](https://en.wikipedia.org/wiki/Langton%27s_ant).

# Usage

`new [rules] [width] [height]`

Create a new turmite simulation with a custom set of rules.

`set_rules [rules]`

Redefine ruleset for current game.

`set_size [width]x[height]`

Redefine window size for current game.

`set_colours [colours*]`

Set colours used in simulation using hex values.

`set_steps [steps]`

Set number of steps simulated on each window refresh.

`from_lospec [palette]`

Set colours from a lospec palette using hyphens in place of spaces.

`list`

List saved turmite simulations.

`load [name]`

Load previous turmite simulation.

`save [name]`

Save current turmite simulation.

`del [name]`

Delete saved turmite simulation.