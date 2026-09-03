from build123d import *

plate_length = 80.0
plate_width = 40.0
plate_thickness = 5.0
slot_width = 20.0
slot_length = 30.0
slot_end_radius = slot_width / 2.0
hole_diameter = 10.0
hole_offset_from_edge = 10.0
rib_width = 5.0
rib_height = 3.0
chamfer_size = 1.0

result = Box(plate_length, plate_width, plate_thickness)
result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

slot_body = Box(slot_width, slot_length - slot_end_radius, plate_thickness)
slot_body = slot_body + Pos(0, (slot_length - slot_end_radius) / 2, 0) * Cylinder(slot_end_radius, plate_thickness)
slot_body = slot_body + Pos(0, -(slot_length - slot_end_radius) / 2, 0) * Cylinder(slot_end_radius, plate_thickness)
result = result - slot_body

hole_x_left = -plate_length / 2 + hole_offset_from_edge
hole_x_right = plate_length / 2 - hole_offset_from_edge
result = result - Pos(hole_x_left, 0, 0) * Cylinder(hole_diameter / 2, plate_thickness)
result = result - Pos(hole_x_right, 0, 0) * Cylinder(hole_diameter / 2, plate_thickness)

rib_z = -plate_thickness / 2 + rib_height / 2
rib = Box(rib_width, rib_width, rib_height)
result = result + Pos(hole_x_left, 0, rib_z) * rib
result = result + Pos(hole_x_right, 0, rib_z) * rib

part = result
part.name = "plate_with_slot_holes_and_ribs"
export_step(part, "output.step")