from build123d import *

block_length = 80.0
block_width = 40.0
block_height = 20.0
corner_fillet_radius = 5.0
central_hole_diameter = 12.0
central_hole_depth = 12.0
m4_hole_diameter = 4.2
m4_hole_spacing = 30.0
m4_hole_offset_y = 15.0
chamfer_distance = 1.0

solid_body = Box(block_length, block_width, block_height)

y_edges = solid_body.edges().filter_by(Axis.Y)
solid_body = fillet(y_edges, corner_fillet_radius)

solid_body = solid_body - Pos(0, 0, block_height/2 - central_hole_depth/2) * Cylinder(central_hole_diameter/2, central_hole_depth)

for x, y in [(-m4_hole_spacing/2, m4_hole_offset_y),
             (m4_hole_spacing/2, m4_hole_offset_y),
             (-m4_hole_spacing/2, -m4_hole_offset_y),
             (m4_hole_spacing/2, -m4_hole_offset_y)]:
    solid_body = solid_body - Pos(x, y, block_height/2) * Cylinder(m4_hole_diameter/2, block_height)

z_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(z_edges, chamfer_distance)

part = solid_body
part.name = "block_with_holes_and_chamfers"
export_step(part, "output.step")