from build123d import *

bracket_length = 80
bracket_width = 40
bracket_thickness = 8
pocket_length = 30
pocket_width = 20
pocket_depth = 4
hole_diameter = 5
hole_spacing_x = 20
hole_spacing_y = 12
hole_rows = 2
hole_cols = 3
fillet_radius = 2
rib_width = 5
rib_height = 12
rib_thickness = 3
rib_spacing = 15

result = Box(bracket_length, bracket_width, bracket_thickness)
result = result - Pos(0, 0, bracket_thickness - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        result = result - Pos(x, y, -bracket_thickness/2) * Cylinder(hole_diameter/2, bracket_thickness + 0.1)

rib_count = int((bracket_length - 2 * rib_spacing) // rib_spacing) + 1
for i in range(rib_count):
    x = (i - (rib_count-1)/2) * rib_spacing
    result = result + Pos(x, 0, bracket_thickness/2) * Box(rib_width, rib_height, rib_thickness)

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

part = result
part.name = "bracket"
export_step(part, "output.step")