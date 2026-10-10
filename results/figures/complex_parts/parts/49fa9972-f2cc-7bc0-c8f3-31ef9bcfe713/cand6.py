from build123d import *

block_width = 50.0
block_depth = 40.0
block_height = 20.0
cyl_radius = 6.0
slot_width = 8.0
slot_depth = 15.0
slot_offset = 5.0
hole_diameter = 6.0
hole_spacing = 24.0
chamfer_size = 1.0

base = Box(block_width, block_depth, block_height)
cyl = Pos(block_width/2, 0, 0) * Cylinder(cyl_radius, block_height)
result = base + cyl

slot = Pos(block_width/2 - slot_width/2, slot_offset, 0) * Box(slot_width, slot_depth, block_height)
result = result - slot

for y in [-hole_spacing/2, hole_spacing/2]:
    result = result - Pos(block_width/2, y, 0) * Cylinder(hole_diameter/2, block_height)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "block_with_cylinder_slot_and_holes"
export_step(part, "output.step")