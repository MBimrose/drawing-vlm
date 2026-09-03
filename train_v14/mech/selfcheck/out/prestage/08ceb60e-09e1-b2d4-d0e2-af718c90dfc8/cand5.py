from build123d import *

block_length = 80.0
block_width = 60.0
block_height = 30.0
rib_width = 20.0
rib_height = 10.0
pocket_length = 40.0
pocket_width = 30.0
pocket_depth = 20.0
hole_diameter = 6.0
hole_spacing = 30.0
fillet_radius = 2.0

base = Pos(0, 0, block_height/2) * Box(block_length, block_width, block_height)
rib = Pos(0, block_width/2 - rib_width/2, rib_height/2) * Box(block_length, rib_width, rib_height)
result = base + rib

pocket = Pos(0, 0, block_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

for x in [-hole_spacing/2, hole_spacing/2]:
    hole = Pos(x, 0, block_height/2) * Cylinder(hole_diameter/2, block_height + 10)
    result = result - hole

result = fillet(result.edges().filter_by(Axis.X), fillet_radius)

part = result
part.name = "block_with_rib_pocket_holes"
export_step(part, "output.step")