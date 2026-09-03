from build123d import *

bracket_length = 80.0
bracket_width = 40.0
bracket_thickness = 8.0
rib_length = 60.0
rib_thickness = 4.0
hole_diameter = 6.0
slot_width = 3.0
slot_length = 14.0
slot_spacing = 20.0
slot_offset_from_edge = 10.0
fillet_radius = 2.0
chamfer_distance = 1.0

solid_body = Box(bracket_length, bracket_width, bracket_thickness)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

rib = Pos(0, -bracket_width/2 - rib_thickness/2, 0) * Box(rib_length, rib_thickness, bracket_thickness)
solid_body = solid_body + rib

solid_body = solid_body - Cylinder(hole_diameter/2, bracket_thickness * 2)

slot_y = bracket_width/2 - slot_offset_from_edge
for i in range(3):
    slot_x = (i - 1) * slot_spacing
    solid_body = solid_body - Pos(slot_x, slot_y, 0) * Box(slot_length, slot_width, bracket_thickness * 2)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

part = solid_body
part.name = "bracket"
export_step(part, "output.step")