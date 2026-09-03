from build123d import *

outer_width = 80.0
outer_depth = 60.0
height = 20.0
wall_thickness = 5.0
inner_width = outer_width - 2 * wall_thickness
inner_depth = outer_depth - 2 * wall_thickness
fillet_radius = 3.0
chamfer_distance = 1.0
hole_diameter = 5.0
hole_offset_x = 15.0
hole_offset_y = 10.0

solid_body = Box(outer_width, outer_depth, height) - Box(inner_width, inner_depth, height)

hole_positions = [
    (hole_offset_x, hole_offset_y),
    (-hole_offset_x, hole_offset_y),
    (hole_offset_x, -hole_offset_y),
    (-hole_offset_x, -hole_offset_y),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter / 2, height)

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)
top_edges = solid_body.edges().sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_distance)

part = solid_body
part.name = "XMountSocket"
export_step(part, "output.step")