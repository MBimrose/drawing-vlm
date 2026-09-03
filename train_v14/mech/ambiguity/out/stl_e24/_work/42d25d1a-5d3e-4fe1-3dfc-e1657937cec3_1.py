from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 20.0
slot_width = 8.0
slot_depth = 12.0
slot_spacing = 20.0
num_slots = 3
fillet_radius = 0.8
chamfer_distance = 1.2
hole_diameter = 4.0
hole_spacing = 20.0
hole_rows = 2
hole_cols = 2

result = Box(block_length, block_width, block_height)

for i in range(num_slots):
    x_pos = (i - (num_slots - 1) / 2) * slot_spacing
    slot = Pos(x_pos, 0, block_height/2 - slot_depth/2) * Box(slot_width, block_width, slot_depth)
    result = result - slot

for i in range(hole_cols):
    for j in range(hole_rows):
        x_pos = (i - (hole_cols - 1) / 2) * hole_spacing
        y_pos = (j - (hole_rows - 1) / 2) * hole_spacing
        hole = Pos(x_pos, y_pos, 0) * Cylinder(hole_diameter/2, block_height)
        result = result - hole

bottom_face = result.faces().sort_by(Axis.Z)[0]
result = chamfer(bottom_face.edges(), chamfer_distance)

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

part = result
part.name = "slot_block_with_holes"
export_step(part, "output.step")