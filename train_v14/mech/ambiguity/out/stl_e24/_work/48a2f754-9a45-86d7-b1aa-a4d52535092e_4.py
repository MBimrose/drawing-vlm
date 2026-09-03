from build123d import *

block_length = 80.0
block_width = 20.0
block_height = 12.0
groove_width = 15.0
groove_depth = 5.0
fillet_radius = 2.0
hole_diameter = 6.4
hole_spacing_x = 30.0
hole_spacing_y = 10.0
pocket_length = 40.0
pocket_width = 12.0
pocket_depth = 6.0

base = Box(block_length, block_width, block_height)
groove = Pos(0, block_width/2 - groove_depth/2, 0) * Box(groove_width, groove_depth, block_height)
result = base - groove
result = fillet(result.edges(), fillet_radius)

pocket = Pos(0, 0, block_height/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

for x, y in [(-hole_spacing_x/2, -hole_spacing_y/2), (hole_spacing_x/2, -hole_spacing_y/2),
             (-hole_spacing_x/2, hole_spacing_y/2), (hole_spacing_x/2, hole_spacing_y/2)]:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, block_height)

part = result
part.name = "grooved_block_with_pocket_and_holes"
export_step(part, "output.step")