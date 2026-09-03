from build123d import *

bracket_length = 80.0
bracket_width = 40.0
bracket_thickness = 8.0
rib_height = 5.0
rib_width = 5.0
rib_spacing = 15.0
hole_diameter = 5.0
hole_depth = 4.0
hole_rows = 2
hole_cols = 3
hole_spacing_x = 20.0
hole_spacing_y = 12.0
fillet_radius = 2.0

solid_body = Box(bracket_length, bracket_width, bracket_thickness)

rib_count = int((bracket_length - 2 * rib_spacing) // rib_spacing) + 1
rib_positions = [(-bracket_length/2 + rib_spacing + i * rib_spacing) for i in range(rib_count)]

for x in rib_positions:
    rib = Pos(x, 0, bracket_thickness/2) * Box(rib_width, rib_height, rib_height)
    solid_body = solid_body + rib

hole_start_x = -((hole_cols - 1) * hole_spacing_x) / 2
hole_start_y = -((hole_rows - 1) * hole_spacing_y) / 2
hole_points = [
    (hole_start_x + i * hole_spacing_x, hole_start_y + j * hole_spacing_y)
    for i in range(hole_cols)
    for j in range(hole_rows)
]

for hx, hy in hole_points:
    hole = Pos(hx, hy, -bracket_thickness/2 + hole_depth/2) * Cylinder(hole_diameter/2, hole_depth + 0.1)
    solid_body = solid_body - hole

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

part = solid_body
part.name = "bracket_with_ribs_and_holes"
export_step(part, "output.step")