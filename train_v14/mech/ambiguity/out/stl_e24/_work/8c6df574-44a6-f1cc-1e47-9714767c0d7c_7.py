from build123d import *

plate_size = 80.0
plate_thickness = 8.0
central_hole_diameter = 20.0
rib_width = 50.0
rib_height = 4.0
corner_hole_diameter = 6.0
corner_hole_counterbore_diameter = 12.0
corner_hole_counterbore_depth = 2.0
corner_hole_offset = 10.0
slot_width = 4.0
slot_length = 20.0
slot_offset = 5.0

result = Box(plate_size, plate_size, plate_thickness)
result = result - Cylinder(central_hole_diameter/2, plate_thickness)

rib = Pos(0, 0, plate_thickness/2 + rib_height/2) * Box(rib_width, rib_width, rib_height)
result = result + rib

corner_positions = [
    (-plate_size/2 + corner_hole_offset, -plate_size/2 + corner_hole_offset),
    (plate_size/2 - corner_hole_offset, -plate_size/2 + corner_hole_offset),
    (-plate_size/2 + corner_hole_offset, plate_size/2 - corner_hole_offset),
    (plate_size/2 - corner_hole_offset, plate_size/2 - corner_hole_offset),
]
for x, y in corner_positions:
    result = result - Pos(x, y, 0) * Cylinder(corner_hole_diameter/2, plate_thickness)
    result = result - Pos(x, y, plate_thickness/2 - corner_hole_counterbore_depth/2) * Cylinder(corner_hole_counterbore_diameter/2, corner_hole_counterbore_depth)

slot_positions = [
    (0, -plate_size/2 + slot_offset),
    (0, plate_size/2 - slot_offset),
    (-plate_size/2 + slot_offset, 0),
    (plate_size/2 - slot_offset, 0),
]
for x, y in slot_positions:
    result = result - Pos(x, y, 0) * Box(slot_width, slot_length, plate_thickness)

part = result
part.name = "plate_with_rib_holes_slots"
export_step(part, "output.step")