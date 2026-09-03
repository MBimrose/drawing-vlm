from build123d import *

outer_width = 80.0
outer_length = 80.0
thickness = 10.0
inner_width = 40.0
inner_length = 40.0
hole_diameter = 5.0
hole_spacing = 20.0
grid_rows = 3
grid_cols = 3
chamfer_size = 0.5

solid_body = Box(outer_width, outer_length, thickness) - Box(inner_width, inner_length, thickness)

points = []
for i in range(grid_cols):
    for j in range(grid_rows):
        x = (i - (grid_cols - 1) / 2) * hole_spacing
        y = (j - (grid_rows - 1) / 2) * hole_spacing
        points.append((x, y))

for x, y in points:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter / 2, thickness * 2)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "plate_with_holes_and_chamfer"
export_step(part, "output.step")