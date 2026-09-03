from build123d import *

bracket_length = 80.0
bracket_width = 40.0
bracket_thickness = 8.0
rib_width = 5.0
rib_height = 12.0
rib_thickness = 1.5
rib_spacing = 15.0
rib_count = 4
hole_diameter = 5.0
hole_spacing_x = 20.0
hole_spacing_y = 12.0
hole_rows = 2
hole_cols = 3
fillet_radius = 2.0

solid_body = Box(bracket_length, bracket_width, bracket_thickness)

for i in range(rib_count):
    x = (i - (rib_count - 1) / 2) * rib_spacing
    rib = Pos(x, 0, bracket_thickness / 2 + rib_thickness / 2) * Box(rib_width, rib_height, rib_thickness)
    solid_body = solid_body + rib

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        hole = Pos(x, y, -bracket_thickness / 2) * Cylinder(hole_diameter / 2, bracket_thickness + 0.01)
        solid_body = solid_body - hole

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

part = solid_body
part.name = "bracket_with_ribs_and_holes"
export_step(part, "output.step")