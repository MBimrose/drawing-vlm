from build123d import *

bracket_length = 60.0
bracket_width = 30.0
bracket_thickness = 5.0
flange_width = 15.0
fillet_radius = 4.0
chamfer_size = 0.8
slot_length = 30.0
slot_width = 10.0
slot_offset_from_front = 5.0
hole_diameter = 4.0
hole_spacing = 20.0
rib_height = 2.0
rib_width = 5.0
rib_length = bracket_length - 10.0

base = Box(bracket_length, bracket_width, bracket_thickness)
flange = Pos(0, bracket_width/2 + flange_width/2, 0) * Box(bracket_length, flange_width, bracket_thickness)
solid_body = base + flange

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

slot_center_y = bracket_width/2 - slot_offset_from_front - slot_width/2
slot = Pos(0, slot_center_y, 0) * Box(slot_length, slot_width, bracket_thickness + 1)
solid_body = solid_body - slot

hole_y = -bracket_width/2 + 10.0
for x in [-hole_spacing/2, hole_spacing/2]:
    solid_body = solid_body - Pos(x, hole_y, 0) * Cylinder(hole_diameter/2, bracket_thickness + 1)

rib = Pos(0, 0, -bracket_thickness/2 + rib_height/2) * Box(rib_length, rib_width, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "bracket"
export_step(part, "output.step")