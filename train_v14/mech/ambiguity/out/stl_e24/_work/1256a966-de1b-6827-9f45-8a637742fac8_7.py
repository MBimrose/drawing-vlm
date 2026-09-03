from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 8.0
rib_width = 5.0
rib_height = 3.0
rib_spacing = 10.0
rib_margin = 5.0
hole_diameter = 6.0
hole_offset_x = 15.0
hole_offset_y = 12.0
chamfer_size = 0.5
slot_length = 60.0
slot_width = 4.0

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

num_ribs = int((plate_length - 2 * rib_margin) // rib_spacing) + 1
for i in range(num_ribs):
    x = (i - (num_ribs - 1) / 2) * rib_spacing
    rib = Pos(x, plate_width / 2 + rib_height / 2, 0) * Box(rib_width, rib_height, plate_thickness)
    solid_body = solid_body + rib

hole_positions = [
    (-plate_length / 2 + hole_offset_x, -plate_width / 2 + hole_offset_y),
    (plate_length / 2 - hole_offset_x, -plate_width / 2 + hole_offset_y),
    (-plate_length / 2 + hole_offset_x, plate_width / 2 - hole_offset_y),
    (plate_length / 2 - hole_offset_x, plate_width / 2 - hole_offset_y),
]
for hx, hy in hole_positions:
    solid_body = solid_body - Pos(hx, hy, 0) * Cylinder(hole_diameter / 2, plate_thickness * 2)

solid_body = solid_body - Box(slot_length, slot_width, plate_thickness * 2)

part = solid_body
part.name = "ribbed_plate_with_holes_and_slot"
export_step(part, "output.step")