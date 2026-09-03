from build123d import *

length = 100.0
width = 30.0
thickness = 5.0
slot_length = 30.0
slot_width = 10.0
hole_diameter = 5.1
hole_spacing = 20.0
chamfer_dist = 2.0
rib_height = 2.0
rib_width = 5.0

solid_body = Box(length, width, thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_dist)

slot = Box(slot_length, slot_width, thickness)
solid_body = solid_body - slot

for i in range(4):
    x = (i - 1.5) * hole_spacing
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(hole_diameter / 2, thickness)

rib = Pos(0, 0, -thickness / 2 - rib_height / 2) * Box(length, rib_width, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "plate_with_slot_holes_and_rib"
export_step(part, "output.step")