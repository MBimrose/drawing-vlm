from build123d import *

block_length = 60.0
block_width = 40.0
block_height = 20.0
hole_diameter = 6.0
hole_spacing_x = 30.0
hole_spacing_y = 20.0
fillet_radius = 2.0
rib_thickness = 4.0
rib_height = 8.0
rib_offset = 5.0
pocket_depth = 6.0
pocket_width = 20.0
pocket_length = 30.0

solid_body = Box(block_length, block_width, block_height)
solid_body = fillet(solid_body.edges(), fillet_radius)

rib = Pos(0, block_width/2 - rib_offset - rib_thickness/2, block_height/2 - rib_height/2) * Box(rib_thickness, rib_height, rib_height)
solid_body = solid_body + rib

pocket = Pos(-block_length/4, -block_width/4, -block_height/2 + pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

hole_positions = [
    (-hole_spacing_x/2, -hole_spacing_y/2),
    ( hole_spacing_x/2, -hole_spacing_y/2),
    (-hole_spacing_x/2,  hole_spacing_y/2),
    ( hole_spacing_x/2,  hole_spacing_y/2),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, block_height * 2)

part = solid_body
part.name = "block_with_rib_pocket_holes"
export_step(part, "output.step")