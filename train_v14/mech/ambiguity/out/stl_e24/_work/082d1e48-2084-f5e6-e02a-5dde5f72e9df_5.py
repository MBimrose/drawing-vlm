from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 30.0
wall_thickness = 5.0
pocket_length = 50.0
pocket_width = 30.0
pocket_depth = block_height - wall_thickness
fillet_radius = 2.0
hole_diameter = 8.0
hole_depth = block_height - 2 * wall_thickness
rib_thickness = 4.0
rib_height = 6.0
rib_width = 20.0
rib_offset = 10.0

solid_body = Box(block_length, block_width, block_height)

pocket = Pos(0, 0, block_height/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

hole = Pos(block_length/2 - hole_depth/2, 0, 0) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, hole_depth)
solid_body = solid_body - hole

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

rib = Pos(-block_length/2 + rib_offset + rib_width/2, 0, -block_height/2 + rib_height/2) * Box(rib_width, rib_thickness, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "block_with_pocket_hole_and_rib"
export_step(part, "output.step")