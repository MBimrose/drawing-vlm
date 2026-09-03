from build123d import *

bracket_width = 80.0
bracket_depth = 40.0
bracket_thickness = 8.0
rib_height = 4.0
rib_width = 70.0
hole_diameter = 6.0
slot_length = 15.0
slot_width = 3.0
slot_spacing = 20.0
slot_offset_y = 10.0
fillet_radius = 2.0
chamfer_distance = 0.5

solid_body = Box(bracket_width, bracket_depth, bracket_thickness)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

rib = Pos(0, -bracket_depth/2 - rib_height/2, 0) * Box(rib_width, rib_height, rib_height)
solid_body = solid_body + rib

solid_body = solid_body - Cylinder(hole_diameter/2, bracket_thickness + 10)

slot_y = bracket_depth/2 - slot_offset_y
for i in range(3):
    slot_x = (i - 1) * slot_spacing
    slot = Pos(slot_x, slot_y, 0) * Box(slot_length, slot_width, bracket_thickness + 10)
    solid_body = solid_body - slot

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

part = solid_body
part.name = "bracket"
export_step(part, "output.step")