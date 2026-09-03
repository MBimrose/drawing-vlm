from build123d import *

bracket_length = 70.0
bracket_width = 30.0
bracket_thickness = 10.0
tab_length = 40.0
tab_height = 12.0
fillet_radius = 2.0
hole_diameter = 5.0
hole_spacing = 30.0
hole_offset_y = 15.0

base = Box(bracket_length, bracket_width, bracket_thickness)
tab = Pos(0, bracket_width/2 + tab_height/2, 0) * Box(tab_length, tab_height, bracket_thickness)
solid_body = base + tab

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

hole_r = hole_diameter / 2
hole_h = bracket_thickness + 2
for x, y in [(-hole_spacing/2, 0), (hole_spacing/2, 0), (0, hole_offset_y)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_r, hole_h)

part = solid_body
part.name = "bracket"
export_step(part, "output.step")