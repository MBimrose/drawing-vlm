from build123d import *

block_length = 80.0
block_width = 60.0
block_height = 30.0
pocket_length = 40.0
pocket_width = 30.0
pocket_depth = 15.0
fillet_radius = 2.0
hole_diameter = 6.0
hole_spacing = 30.0
rib_height = 5.0
rib_thickness = 4.0
rib_offset = 20.0

solid_body = Box(block_length, block_width, block_height)

pocket = Pos(0, 0, block_height/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

x_edges = solid_body.edges().filter_by(Axis.X)
solid_body = fillet(x_edges, fillet_radius)

for x, y in [(-hole_spacing/2, 0), (hole_spacing/2, 0)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, block_height)

rib = Pos(0, 0, -block_height/2 + rib_height/2) * Box(block_length - 2*rib_offset, rib_thickness, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "block_with_pocket_holes_and_rib"
export_step(part, "output.step")