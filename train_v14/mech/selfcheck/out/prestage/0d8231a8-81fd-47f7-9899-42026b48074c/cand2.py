from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 30.0
wall_thickness = 4.0
chamfer_size = 1.0
hole_diameter = 5.0
hole_spacing = 20.0
hole_count = 3

solid = Box(block_width, block_length, block_height)
solid = chamfer(solid.edges(), chamfer_size)

for i in range(hole_count):
    x = (i - (hole_count - 1) / 2) * hole_spacing
    solid = solid - Pos(x, 0, 0) * Cylinder(hole_diameter / 2, block_height + 10)

part = solid
part.name = "chamfered_block_with_holes"
export_step(part, "output.step")