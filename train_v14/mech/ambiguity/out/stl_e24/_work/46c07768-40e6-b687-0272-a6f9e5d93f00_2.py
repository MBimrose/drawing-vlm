from build123d import *

plate_length = 80.0
plate_width = 40.0
plate_thickness = 5.0
slot_width = 20.0
slot_length = 30.0
slot_end_radius = slot_width / 2.0
hole_diameter = 10.0
hole_offset = 30.0
rib_width = 5.0
rib_height = 3.0
rib_offset = 5.0
chamfer_size = 1.0

base = Box(plate_length, plate_width, plate_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)

slot_body = Box(slot_width, slot_length - slot_width, plate_thickness)
slot_body = slot_body + Pos(0, (slot_length - slot_width) / 2, 0) * Cylinder(slot_end_radius, plate_thickness)
slot_body = slot_body + Pos(0, -(slot_length - slot_width) / 2, 0) * Cylinder(slot_end_radius, plate_thickness)

result = base - slot_body

for x in [-hole_offset, hole_offset]:
    result = result - Pos(x, 0, 0) * Cylinder(hole_diameter / 2, plate_thickness)

rib = Box(rib_width, plate_width - 2 * rib_offset, rib_height)
rib_z = -plate_thickness / 2 + rib_height / 2
rib_left = Pos(-plate_length / 2 + rib_offset + rib_width / 2, 0, rib_z) * rib
rib_right = Pos(plate_length / 2 - rib_offset - rib_width / 2, 0, rib_z) * rib

result = result + rib_left + rib_right

part = result
part.name = "plate_with_slot_holes_and_ribs"
export_step(part, "output.step")