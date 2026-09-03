from build123d import *

block_width = 60.0
block_depth = 40.0
block_height = 20.0
pocket_width = 30.0
pocket_depth = 20.0
pocket_depth_height = 10.0
fillet_radius = 2.0
hole_diameter = 6.0
hole_spacing_x = 30.0
hole_spacing_y = 20.0

solid_body = Pos(0, 0, block_height/2) * Box(block_width, block_depth, block_height)
solid_body = fillet(solid_body.edges(), fillet_radius)

pocket = Pos(-pocket_width/2, -pocket_depth/2, pocket_depth_height/2) * Box(pocket_width, pocket_depth, pocket_depth_height)
solid_body = solid_body - pocket

hole_r = hole_diameter / 2
for x in [-hole_spacing_x/2, hole_spacing_x/2]:
    for y in [-hole_spacing_y/2, hole_spacing_y/2]:
        solid_body = solid_body - Pos(x, y, block_height/2) * Cylinder(hole_r, block_height)

part = solid_body
part.name = "block_with_pocket_and_holes"
export_step(part, "output.step")