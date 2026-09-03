from build123d import *

plate_width = 80.0
plate_length = 80.0
plate_thickness = 8.0
rib_width = 40.0
rib_length = 40.0
rib_height = 4.0
central_hole_dia = 20.0
corner_hole_dia = 6.0
corner_hole_offset = 10.0
counterbore_radius = 3.0
counterbore_outer = 6.0
counterbore_depth = 2.0
slot_width = 4.0
slot_length = 20.0
chamfer_size = 0.5

base = Pos(0, 0, plate_thickness/2) * Box(plate_width, plate_length, plate_thickness)
rib = Pos(0, 0, plate_thickness + rib_height/2) * Box(rib_width, rib_length, rib_height)
result = base + rib

total_height = plate_thickness + rib_height
result = result - Pos(0, 0, total_height/2) * Cylinder(central_hole_dia/2, total_height)

corner_positions = [
    (plate_width/2 - corner_hole_offset, plate_length/2 - corner_hole_offset),
    (-plate_width/2 + corner_hole_offset, plate_length/2 - corner_hole_offset),
    (-plate_width/2 + corner_hole_offset, -plate_length/2 + corner_hole_offset),
    (plate_width/2 - corner_hole_offset, -plate_length/2 + corner_hole_offset),
]
for x, y in corner_positions:
    result = result - Pos(x, y, total_height/2) * Cylinder(corner_hole_dia/2, total_height)
    result = result - Pos(x, y, total_height - counterbore_depth/2) * Cylinder(counterbore_outer, counterbore_depth)

slot_positions = [
    (0, plate_length/2 - slot_width/2),
    (0, -plate_length/2 + slot_width/2),
    (plate_width/2 - slot_width/2, 0),
    (-plate_width/2 + slot_width/2, 0),
]
for x, y in slot_positions:
    result = result - Pos(x, y, plate_thickness/2) * Box(slot_width, slot_length, plate_thickness)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "plate_with_rib_holes_slots"
export_step(part, "output.step")