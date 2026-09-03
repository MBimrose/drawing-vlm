from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 40.0
hole_diameter = 5.0
hole_depth = 30.0

base = Box(block_length, block_width, block_height)
hole = Pos(0, 0, -block_height/2 + hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)
part = base - hole
part.name = "block_with_hole"
export_step(part, "output.step")