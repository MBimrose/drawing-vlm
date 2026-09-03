from build123d import *

block_length = 80
block_width = 50
block_height = 40

base = Box(block_length, block_width, block_height)
hole = Cylinder(2.5, block_height + 20)
part = base - hole
part.name = "block_with_hole"
export_step(part, "output.step")