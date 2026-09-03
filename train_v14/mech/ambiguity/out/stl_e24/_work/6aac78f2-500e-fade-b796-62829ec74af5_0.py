from build123d import *

bracket_length = 80.0
bracket_width = 60.0
bracket_thickness = 10.0
wall_thickness = 1.0
chamfer_distance = 2.0
slot_width = 5.0
slot_length = 40.0
groove_width = 4.0
groove_length = 30.0
groove_offset = 12.0
hole_diameter = 4.0
hole_cbore_diameter = 6.0
hole_cbore_depth = 2.0
hole_spacing = 20.0
rib_width = 15.0
rib_length = 35.0
rib_height = 4.0
rib_offset = 10.0

solid_body = Box(bracket_length, bracket_width, bracket_thickness)
solid_body = offset(solid_body, amount=-wall_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

slot = Box(slot_length, slot_width, bracket_thickness + 2)
solid_body = solid_body - slot

groove = Pos(0, groove_offset, 0) * Box(groove_length, groove_width, bracket_thickness / 2)
solid_body = solid_body - groove

for y in [-hole_spacing / 2, hole_spacing / 2]:
    cbore = Pos(bracket_length / 2 - hole_cbore_depth / 2, y, 0) * Rot(0, 90, 0) * Cylinder(hole_cbore_diameter / 2, hole_cbore_depth)
    shaft = Pos(0, y, 0) * Rot(0, 90, 0) * Cylinder(hole_diameter / 2, bracket_length + 2)
    solid_body = solid_body - cbore - shaft

rib = Pos(0, rib_offset, 0) * Box(rib_length, rib_width, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "bracket"
export_step(part, "output.step")