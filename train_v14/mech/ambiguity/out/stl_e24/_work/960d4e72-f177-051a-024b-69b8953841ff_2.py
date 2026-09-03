from build123d import *

block_length = 80.0
block_width = 40.0
block_height = 20.0
bearing_radius = 12.0
bearing_depth = 8.0
bearing_offset_x = block_length / 2 - bearing_depth / 2
hole_diameter = 5.0
hole_spacing = 30.0

base = Box(block_length, block_width, block_height)
bearing_cut = Pos(bearing_offset_x, 0, 0) * Rot(0, 90, 0) * Cylinder(bearing_radius, bearing_depth)
result = base - bearing_cut

for x, y in [(-hole_spacing/2, -hole_spacing/2), (hole_spacing/2, -hole_spacing/2),
             (-hole_spacing/2, hole_spacing/2), (hole_spacing/2, hole_spacing/2)]:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, block_height * 2)

part = result
part.name = "bearing_block"
export_step(part, "output.step")