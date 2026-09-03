from build123d import *

outer_width = 80.0
outer_height = 60.0
frame_thickness = 5.0
extrude_depth = 20.0
chamfer_size = 2.0
hole_diameter = 5.0
hole_spacing_x = 20.0
hole_spacing_y = 20.0
num_holes_x = 3
num_holes_y = 2

inner_width = outer_width - 2 * frame_thickness
inner_height = outer_height - 2 * frame_thickness

solid_body = Box(outer_width, outer_height, extrude_depth)
solid_body = solid_body - Box(inner_width, inner_height, extrude_depth)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

x_start = -((num_holes_x - 1) * hole_spacing_x) / 2.0
y_start = -((num_holes_y - 1) * hole_spacing_y) / 2.0
hole_points = []
for i in range(num_holes_x):
    for j in range(num_holes_y):
        x = x_start + i * hole_spacing_x
        y = y_start + j * hole_spacing_y
        hole_points.append((x, y))

for x, y in hole_points:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter / 2, extrude_depth * 2)

part = solid_body
part.name = "frame_with_holes"
export_step(part, "output.step")