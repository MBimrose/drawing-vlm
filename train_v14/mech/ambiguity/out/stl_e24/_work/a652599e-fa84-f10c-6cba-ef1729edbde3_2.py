from build123d import *

block_length = 80.0
block_width = 40.0
block_height = 20.0
corner_fillet_radius = 5.0
blind_hole_diameter = 12.0
blind_hole_depth = 10.0
through_hole_diameter = 4.2
through_hole_spacing = 30.0
rib_width = 6.0
rib_height = 4.0
chamfer_distance = 1.0

solid_body = Box(block_length, block_width, block_height)

y_edges = solid_body.edges().filter_by(Axis.Y)
solid_body = fillet(y_edges, corner_fillet_radius)

solid_body = solid_body - Pos(0, 0, block_height/2 - blind_hole_depth/2) * Cylinder(blind_hole_diameter/2, blind_hole_depth)

for x, y in [(-through_hole_spacing/2, -through_hole_spacing/2),
             (through_hole_spacing/2, -through_hole_spacing/2),
             (-through_hole_spacing/2, through_hole_spacing/2),
             (through_hole_spacing/2, through_hole_spacing/2)]:
    solid_body = solid_body - Pos(x, y, block_height/2) * Cylinder(through_hole_diameter/2, block_height)

rib = Box(block_length, rib_width, rib_height)
solid_body = solid_body + Pos(0, 0, -block_height/2 + rib_height/2) * rib
solid_body = solid_body + Pos(0, 0, block_height/2 - rib_height/2) * rib

z_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(z_edges, chamfer_distance)

part = solid_body
part.name = "block_with_ribs_and_holes"
export_step(part, "output.step")