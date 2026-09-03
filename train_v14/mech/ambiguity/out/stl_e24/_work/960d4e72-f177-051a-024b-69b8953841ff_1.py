from build123d import *

block_length = 80.0
block_width = 40.0
block_height = 20.0
bearing_radius = 12.0
bearing_depth = 8.0
hole_diameter = 5.0
hole_spacing = 30.0

result = Box(block_length, block_width, block_height)

bearing_cut = Pos(block_length/2, 0, 0) * Rot(0, 90, 0) * Cylinder(bearing_radius, bearing_depth)
result = result - bearing_cut

hole_positions = [
    (-hole_spacing/2, -hole_spacing/2),
    (hole_spacing/2, -hole_spacing/2),
    (-hole_spacing/2, hole_spacing/2),
    (hole_spacing/2, hole_spacing/2),
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, block_height)

part = result
part.name = "block_with_bearing_and_holes"
export_step(part, "output.step")