from build123d import *

block_width = 80.0
block_depth = 50.0
block_height = 20.0
fillet_radius = 3.0
chamfer_distance = 1.0
hole_diameter = 10.0
hole_depth = 10.0
hole_spacing = 30.0
rib_width = 20.0
rib_depth = 5.0
rib_height = 5.0
side_pocket_width = 10.0
side_pocket_depth = 15.0
side_pocket_height = 10.0

solid_body = Box(block_width, block_depth, block_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

rib = Pos(0, 0, block_height + rib_height/2) * Box(rib_width, rib_depth, rib_height)
solid_body = solid_body + rib

pocket = Pos(-block_width/2 + side_pocket_width/2, 0, block_height/2) * Box(side_pocket_width, side_pocket_depth, side_pocket_height)
solid_body = solid_body - pocket

for x in [-hole_spacing/2, hole_spacing/2]:
    hole = Pos(x, 0, block_height/2 - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)
    solid_body = solid_body - hole

part = solid_body
part.name = "block_with_rib_pocket_holes"
export_step(part, "output.step")