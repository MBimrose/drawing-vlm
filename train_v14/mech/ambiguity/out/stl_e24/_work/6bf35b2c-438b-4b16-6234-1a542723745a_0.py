from build123d import *

bracket_length = 80.0
bracket_width = 40.0
bracket_thickness = 8.0
rib_height = 12.0
rib_width = 5.0
rib_spacing = 15.0
rib_margin = 10.0
rib_thickness = 3.0
hole_diameter = 5.0
hole_spacing_x = 20.0
hole_spacing_y = 12.0
hole_rows = 2
hole_cols = 3
fillet_radius = 2.0

solid_body = Box(bracket_length, bracket_width, bracket_thickness)

rib_count = int((bracket_length - 2 * rib_margin) / rib_spacing) + 1
for i in range(rib_count):
    x = -bracket_length/2 + rib_margin + i * rib_spacing
    rib = Pos(x, 0, bracket_thickness/2) * Box(rib_width, rib_height, rib_thickness)
    solid_body = solid_body + rib

for col in range(hole_cols):
    for row in range(hole_rows):
        x = (col - (hole_cols-1)/2) * hole_spacing_x
        y = (row - (hole_rows-1)/2) * hole_spacing_y
        hole = Pos(x, y, -bracket_thickness/2) * Cylinder(hole_diameter/2, bracket_thickness + 0.1)
        solid_body = solid_body - hole

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

part = solid_body
part.name = "bracket_with_ribs_and_holes"
export_step(part, "output.step")