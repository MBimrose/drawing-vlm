from build123d import *

plate_length = 100.0
plate_width = 30.0
plate_thickness = 5.0
slot_length = 30.0
slot_width = 10.0
hole_diameter = 5.1
hole_spacing = 20.0
hole_count = 4
chamfer_distance = 2.0
rib_length = 20.0
rib_width = 5.0
rib_height = 2.0
rib_offset = 5.0

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

slot = Box(slot_length, slot_width, plate_thickness)
solid_body = solid_body - slot

for i in range(hole_count):
    x = (i - (hole_count - 1) / 2) * hole_spacing
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(hole_diameter / 2, plate_thickness)

rib1 = Pos(-plate_length / 2 + rib_offset + rib_length / 2, -plate_width / 2 + rib_width / 2, -plate_thickness / 2 - rib_height / 2) * Box(rib_length, rib_width, rib_height)
rib2 = Pos(plate_length / 2 - rib_offset - rib_length / 2, -plate_width / 2 + rib_width / 2, -plate_thickness / 2 - rib_height / 2) * Box(rib_length, rib_width, rib_height)

solid_body = solid_body + rib1 + rib2

part = solid_body
part.name = "plate_with_slot_holes_and_ribs"
export_step(part, "output.step")