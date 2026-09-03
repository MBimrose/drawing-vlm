from build123d import *

bracket_length = 70
bracket_width = 30
bracket_thickness = 10
tab_length = 40
tab_width = 12
fillet_radius = 2
hole_diameter = 5
hole_spacing_x = 30
hole_spacing_y = 20
hole_offset_x = 20
hole_offset_y = 15

base = Box(bracket_length, bracket_width, bracket_thickness)
tab = Pos(0, bracket_width/2 + tab_width/2, 0) * Box(tab_length, tab_width, bracket_thickness)
solid_body = base + tab

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

hole_positions = [
    (-hole_offset_x, -hole_offset_y),
    (hole_offset_x, -hole_offset_y),
    (-hole_offset_x, hole_offset_y),
    (hole_offset_x, hole_offset_y),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, bracket_thickness * 2)

part = solid_body
part.name = "bracket_with_tab"
export_step(part, "output.step")