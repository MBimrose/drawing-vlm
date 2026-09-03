from build123d import *

outer_size = 80.0
inner_size = 40.0
thickness = 10.0
hole_diameter = 5.0
corner_hole_offset = 15.0
mid_hole_offset = 25.0
chamfer_size = 0.5

solid_body = Box(outer_size, outer_size, thickness) - Box(inner_size, inner_size, thickness)

hole_positions = [
    (outer_size/2 - corner_hole_offset, outer_size/2 - corner_hole_offset),
    (-outer_size/2 + corner_hole_offset, outer_size/2 - corner_hole_offset),
    (-outer_size/2 + corner_hole_offset, -outer_size/2 + corner_hole_offset),
    (outer_size/2 - corner_hole_offset, -outer_size/2 + corner_hole_offset),
    (0, outer_size/2 - mid_hole_offset),
    (0, -outer_size/2 + mid_hole_offset),
    (outer_size/2 - mid_hole_offset, 0),
    (-outer_size/2 + mid_hole_offset, 0),
]

for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, thickness)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "SquarePlateWithHoles"
export_step(part, "output.step")