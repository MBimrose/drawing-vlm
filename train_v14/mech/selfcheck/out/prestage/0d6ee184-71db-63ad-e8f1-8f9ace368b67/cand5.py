from build123d import *

bracket_length = 70.0
bracket_width = 30.0
bracket_thickness = 10.0
tab_length = 40.0
tab_width = 12.0
hole_diameter = 5.0
hole_offset_x = 20.0
hole_offset_y = 15.0
fillet_radius = 2.0

base = Box(bracket_length, bracket_width, bracket_thickness)
tab = Pos(0, bracket_width/2 + tab_width/2, 0) * Box(tab_length, tab_width, bracket_thickness)
solid_body = base + tab

hole_positions = [
    (-bracket_length/2 + hole_offset_x, -bracket_width/2 + hole_offset_y),
    (bracket_length/2 - hole_offset_x, -bracket_width/2 + hole_offset_y),
    (0, bracket_width/2 + tab_width/2)
]

for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, bracket_thickness * 2)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

part = solid_body
part.name = "bracket_with_tab"
export_step(part, "output.step")