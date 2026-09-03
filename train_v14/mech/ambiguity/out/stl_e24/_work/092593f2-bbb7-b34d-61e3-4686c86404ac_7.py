from build123d import *

plate_length = 80.0
plate_width = 40.0
plate_thickness = 4.0
slot_width = 20.0
slot_length = 28.0
slot_offset_from_edge = 5.0
slot_fillet_radius = 2.0
mount_hole_diameter = 5.0
mount_hole_offset = 8.0
rib_height = 6.0
rib_thickness = 2.0
rib_length = 30.0

base = Box(plate_length, plate_width, plate_thickness)

slot_center_x = plate_length / 2 - slot_offset_from_edge - slot_width / 2
slot_solid = Pos(slot_center_x, 0, 0) * Box(slot_width, slot_length, plate_thickness)
slot_solid = fillet(slot_solid.edges().filter_by(Axis.Z), slot_fillet_radius)

result = base - slot_solid

hole_x = -plate_length / 2 + mount_hole_offset
hole_y_offset = plate_width / 2 - mount_hole_offset
for y in [hole_y_offset, -hole_y_offset]:
    result = result - Pos(hole_x, y, 0) * Cylinder(mount_hole_diameter / 2, plate_thickness)

rib = Pos(plate_length / 2 + rib_height / 2, 0, 0) * Box(rib_height, rib_length, rib_thickness)
result = result + rib

part = result
part.name = "plate_with_slot_holes_and_rib"
export_step(part, "output.step")