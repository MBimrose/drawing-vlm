from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 40.0
hole_diameter = 5.0

solid_body = Box(block_length, block_width, block_height)
solid_body = solid_body - Cylinder(hole_diameter / 2, block_height + 20)

part = solid_body
part.name = "block_with_hole"
export_step(part, "output.step")