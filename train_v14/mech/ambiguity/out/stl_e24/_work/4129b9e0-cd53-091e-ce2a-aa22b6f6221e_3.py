from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 20.0
corner_fillet_radius = 3.0
hole_diameter = 10.0
hole_spacing = 30.0
rib_height = 5.0
rib_width = 5.0
rib_length = 20.0
pocket_width = 10.0
pocket_depth = 15.0
pocket_height = 8.0
chamfer_distance = 1.0

solid_body = Box(block_length, block_width, block_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), corner_fillet_radius)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

for x in [-hole_spacing/2, hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, block_height/2) * Cylinder(hole_diameter/2, block_height)

rib = Pos(0, 0, block_height + rib_height/2) * Box(rib_length, rib_width, rib_height)
solid_body = solid_body + rib

pocket = Pos(-block_length/2 + pocket_width/2, 0, block_height - pocket_height/2) * Box(pocket_width, pocket_depth, pocket_height)
solid_body = solid_body - pocket

part = solid_body
part.name = "filleted_block_with_holes_rib_pocket"
export_step(part, "output.step")