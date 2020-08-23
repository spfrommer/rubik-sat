# rubik-sat
## Azzam Al & Samuel Pfrommer

#### Setup and execution
This is a `python3` project. The only dependencies are `matplotlib` and `ortools`, which can be installed as follows:

`pip install matplotlib ortools`

As a frontend for the solver we use the [magic cube library](https://github.com/davidwhogg/MagicCube) by David Hogg. To execute run:

`python magic/cube_interactive.py 2`

Changing 2 to 3 gives a 3x3x3 cube; however, due to the NP-hardness of the problem 3x3x3 cubes can only handle up to about 8 scrambles. Hitting the solve button runs our solver under the hood.

#### Solver
We implemented optimal Rubik's cube solving as a constraint programming problem using Google's OR-tools. Each state is represented by a set of integer variables ranging from 0 to 5, corresponding to each color. We add a move variable between each pair of states and constraints implying facelet mappings. Final states correspond to each face having a uniform color, and as an objective we minimize the number of moves to get to a final state.

The algorithm can handle 3x3x3 cubes with an optimal solving length of 8 or fewer. For 2x2x2 cubes, we can optimize the solving process by noting that opposite face moves are equivalent, halving the move search space from 18 to 9. This allows efficient solving of arbitrarily scrambled 2x2x2 cubes.

## Overview of File Structure
- **magic/** contains python code for visualizing a cube (modified from magic cube library).
- **rubiks.py** defines the RubiksCube class, various helper classes, and facelet relationships for moves
- **solver.py** outputs a list of moves to solve a particular instance of RubiksCube

You will also need ortools and matplotlib for python3. 
