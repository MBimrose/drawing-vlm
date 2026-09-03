from build123d import *

block_length = 80.0
block_width = 30.0
block_height = 10.0
pocket_width = 20.0
pocket_length = 25.0
pocket_depth = 2.0
fillet_radius = 2.0
chamfer_distance = 0.5
hole_diameter = 3.3
hole_spacing_x = 40.0
hole_spacing_y = 20.0
rib_thickness = 2.0
rib_height = 5.0
rib_width = 10.0

solid_body = Box(block_length, block_width, block_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_distance)

pocket = Pos(0, 0, block_height/2 - pocket_depth/2) * Box(pocket_width, pocket_length, pocket_depth)
solid_body = solid_body - pocket

for x, y in [(-hole_spacing_x/2, -hole_spacing_y/2), (hole_spacing_x/2, -hole_spacing_y/2),
             (-hole_spacing_x/2, hole_spacing_y/2), (hole_spacing_x/2, hole_spacing_y/2)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, block_height + 1)

rib = Pos(0, 0, -block_height/2 + rib_height/2) * Box(rib_width, rib_thickness, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "block_with_pocket_holes_and_rib"
export_step(part, "output.step")