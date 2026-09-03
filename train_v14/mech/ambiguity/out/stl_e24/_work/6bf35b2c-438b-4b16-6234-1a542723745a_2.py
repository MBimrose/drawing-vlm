from build123d import *

bracket_length = 80.0
bracket_width = 40.0
bracket_thickness = 8.0
rib_height = 12.0
rib_width = 5.0
rib_thickness = 1.5
rib_spacing = 15.0
rib_count = int((bracket_length - rib_spacing) // rib_spacing)
hole_diameter = 5.0
hole_spacing_x = 20.0
hole_spacing_y = 12.0
hole_rows = 2
hole_cols = 3
fillet_radius = 2.0

result = Box(bracket_length, bracket_width, bracket_thickness)

for i in range(rib_count):
    x = (i - (rib_count - 1) / 2) * rib_spacing
    rib = Pos(x, 0, bracket_thickness / 2 + rib_thickness / 2) * Box(rib_width, rib_height, rib_thickness)
    result = result + rib

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        hole = Pos(x, y, -bracket_thickness / 2) * Cylinder(hole_diameter / 2, bracket_thickness + 0.1)
        result = result - hole

vertical_edges = result.edges().filter_by(Axis.Z)
result = fillet(vertical_edges, fillet_radius)

part = result
part.name = "bracket_with_ribs_and_holes"
export_step(part, "output.step")