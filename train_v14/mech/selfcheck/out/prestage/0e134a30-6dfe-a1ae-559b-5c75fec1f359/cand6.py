from build123d import *

plate_length = 80
plate_width = 60
plate_thickness = 15
groove_width = 5
groove_depth = 4
slot_length = 30
slot_width = 10
hole_diameter = 5
hole_offset_x = 20
hole_offset_y = 15

result = Box(plate_length, plate_width, plate_thickness)

groove = Pos(0, 0, plate_thickness/2 - groove_depth/2) * Box(plate_length - 2*groove_width, plate_width - 2*groove_width, groove_depth)
result = result - groove

slot = Box(slot_length, slot_width, plate_thickness)
result = result - slot

for x, y in [(-hole_offset_x, -hole_offset_y), (hole_offset_x, -hole_offset_y), (-hole_offset_x, hole_offset_y), (hole_offset_x, hole_offset_y)]:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)

part = result
part.name = "plate_with_groove_slot_holes"
export_step(part, "output.step")