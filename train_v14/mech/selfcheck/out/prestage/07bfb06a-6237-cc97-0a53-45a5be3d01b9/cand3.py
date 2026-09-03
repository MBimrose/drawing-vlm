from build123d import *

plate_width = 80.0
plate_height = 60.0
plate_thickness = 6.0
corner_fillet_radius = 2.0
opening_width = 30.0
opening_height = 20.0
slot_length = 20.0
slot_width = 5.0
slot_offset_from_edge = 10.0

solid_body = Box(plate_width, plate_height, plate_thickness)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_fillet_radius)

solid_body = solid_body - Box(opening_width, opening_height, plate_thickness)

slot_center_x = -plate_width / 2 + slot_offset_from_edge
slot_shape = SlotOverall(slot_length, slot_width)
solid_body = solid_body - Pos(slot_center_x, 0, 0) * extrude(slot_shape, amount=plate_thickness)

part = solid_body
part.name = "plate_with_opening_and_slot"
export_step(part, "output.step")