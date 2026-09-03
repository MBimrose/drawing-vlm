from build123d import *

bracket_length = 80.0
bracket_width = 40.0
bracket_thickness = 8.0
slot_length = 15.0
slot_width = 3.0
slot_spacing = 20.0
num_slots = 3
fillet_radius = 2.0
chamfer_distance = 0.5
hole_diameter = 6.0
rib_height = 4.0
rib_thickness = 5.0
rib_offset = 5.0

solid_body = Box(bracket_length, bracket_width, bracket_thickness)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

slot_y = bracket_width / 2 - slot_width / 2 - 2
for i in range(num_slots):
    x = (i - (num_slots - 1) / 2) * slot_spacing
    slot = Pos(x, slot_y, 0) * Box(slot_length, slot_width, bracket_thickness)
    solid_body = solid_body - slot

solid_body = solid_body - Cylinder(hole_diameter / 2, bracket_thickness)

rib = Pos(0, -bracket_width / 2 - rib_height / 2, 0) * Box(bracket_length - 2 * rib_offset, rib_height, rib_thickness)
solid_body = solid_body + rib

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

part = solid_body
part.name = "bracket_with_slots_and_rib"
export_step(part, "output.step")