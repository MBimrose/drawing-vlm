from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 8.0
rib_height = 3.0
rib_width = 4.0
rib_spacing = 8.0
hole_diameter = 6.0
hole_offset_x = 15.0
hole_offset_y = 12.0
slot_length = 60.0
slot_width = 4.0
chamfer_size = 0.5

rib_count = int(plate_length / rib_spacing)

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

for i in range(rib_count):
    x = (i - (rib_count - 1) / 2) * rib_spacing
    rib = Pos(x, plate_width / 2 + rib_height / 2, 0) * Box(rib_width, rib_height, plate_thickness)
    solid_body = solid_body + rib

hole_positions = [
    (-plate_length / 2 + hole_offset_x, -plate_width / 2 + hole_offset_y),
    (plate_length / 2 - hole_offset_x, -plate_width / 2 + hole_offset_y),
    (-plate_length / 2 + hole_offset_x, plate_width / 2 - hole_offset_y),
    (plate_length / 2 - hole_offset_x, plate_width / 2 - hole_offset_y),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter / 2, plate_thickness * 2)

solid_body = solid_body - Box(slot_length, slot_width, plate_thickness * 2)

part = solid_body
part.name = "ribbed_plate_with_holes_and_slot"
export_step(part, "output.step")