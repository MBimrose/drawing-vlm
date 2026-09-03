from build123d import *

block_length = 70.0
block_width = 40.0
block_height = 12.0
rib_width = 20.0
rib_length = 30.0
rib_height = 4.0
hole_diameter = 6.0
hole_depth = 8.0
fillet_radius = 4.0
chamfer_distance = 0.8
pocket_width = 10.0
pocket_height = 8.0
pocket_depth = 8.0

solid_body = Box(block_length, block_width, block_height)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
fillet_edges = [e for e in vertical_edges if e.center().Y > 0]
solid_body = fillet(fillet_edges, fillet_radius)

rib = Pos(0, 0, rib_height/2) * Box(rib_width, rib_length, rib_height)
solid_body = solid_body + rib

hole_spacing = block_length / 4
hole_positions = [(-hole_spacing, 0), (0, 0), (hole_spacing, 0)]
for x, y in hole_positions:
    hole = Pos(x, y, block_height/2 - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)
    solid_body = solid_body - hole

pocket = Pos(block_length/2 - pocket_depth/2, 0, 0) * Box(pocket_depth, pocket_width, pocket_height)
solid_body = solid_body - pocket

bottom_edges = solid_body.edges().filter_by(Axis.X).sort_by(Axis.Z)[:2]
solid_body = chamfer(bottom_edges, chamfer_distance)

part = solid_body
part.name = "block_with_rib_holes_pocket"
export_step(part, "output.step")