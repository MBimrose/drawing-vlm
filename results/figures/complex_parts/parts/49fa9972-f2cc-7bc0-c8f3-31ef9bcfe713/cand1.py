from build123d import *

block_length = 50.0
block_width = 40.0
block_height = 20.0
cap_radius = 5.0
pocket_width = 10.0
pocket_depth = 15.0
hole_diameter = 6.0
hole_spacing = 24.0
hole_offset_x = 12.0
chamfer_size = 1.0

base = Box(block_length, block_width, block_height)
cap = Pos(block_length/2, 0, 0) * Cylinder(cap_radius, block_height)
result = base + cap

pocket = Pos(block_length/2, 0, 0) * Box(pocket_width, pocket_depth, block_height)
result = result - pocket

for y in [-hole_spacing/2, hole_spacing/2]:
    result = result - Pos(hole_offset_x, y, 0) * Cylinder(hole_diameter/2, block_height)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "block_with_cap_pocket_holes"
export_step(part, "output.step")