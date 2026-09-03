from build123d import *

block_length = 80.0
block_width = 60.0
block_height = 15.0
groove_width = 5.0
groove_depth = 4.0
hole_diameter = 5.0
hole_offset_x = 20.0
hole_offset_y = 15.0
slot_length = 30.0
slot_width = 10.0

result = Box(block_length, block_width, block_height)

groove = Pos(0, 0, block_height/2 - groove_depth/2) * Box(block_length - 2*groove_width, block_width - 2*groove_width, groove_depth)
result = result - groove

for x, y in [(-hole_offset_x, -hole_offset_y), (hole_offset_x, -hole_offset_y), (-hole_offset_x, hole_offset_y), (hole_offset_x, hole_offset_y)]:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, block_height)

slot = Box(slot_length, slot_width, block_height)
result = result - slot

part = result
part.name = "grooved_block_with_holes_and_slot"
export_step(part, "output.step")