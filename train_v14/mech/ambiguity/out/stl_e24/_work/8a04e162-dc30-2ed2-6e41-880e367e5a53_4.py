from build123d import *

bracket_length = 80
bracket_width = 40
bracket_thickness = 8
slot_length = 15
slot_width = 3
slot_spacing = 20
slot_offset_y = 10
fillet_radius = 2
chamfer_distance = 0.5
hole_diameter = 6
rib_height = 4
rib_thickness = 5
rib_offset = 5

solid_body = Box(bracket_length, bracket_width, bracket_thickness)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)
solid_body = solid_body - Cylinder(hole_diameter/2, bracket_thickness * 2)

slot_positions = [(-slot_spacing, slot_offset_y), (0, slot_offset_y), (slot_spacing, slot_offset_y)]
for x, y in slot_positions:
    solid_body = solid_body - Pos(x, y, 0) * Box(slot_length, slot_width, bracket_thickness * 2)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

rib = Pos(0, -bracket_width/2 - rib_height/2, 0) * Box(bracket_length - 2*rib_offset, rib_height, rib_thickness)
solid_body = solid_body + rib

part = solid_body
part.name = "bracket_with_slots_and_rib"
export_step(part, "output.step")