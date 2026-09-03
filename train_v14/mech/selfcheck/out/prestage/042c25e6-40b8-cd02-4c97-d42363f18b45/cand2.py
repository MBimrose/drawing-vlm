from build123d import *

block_width = 60.0
block_depth = 40.0
block_height = 20.0
pocket_width = 30.0
pocket_depth = 20.0
pocket_depth_cut = 8.0
hole_diameter = 6.0
hole_spacing_x = 30.0
hole_spacing_y = 20.0
fillet_radius = 2.0
notch_width = 10.0
notch_depth = 15.0
notch_height = 5.0

solid_body = Box(block_width, block_depth, block_height)
solid_body = fillet(solid_body.edges(), fillet_radius)

pocket = Pos(0, 0, block_height - pocket_depth_cut/2) * Box(pocket_width, pocket_depth, pocket_depth_cut)
solid_body = solid_body - pocket

notch = Pos(-block_width/2 + notch_width/2, -block_depth/2 + notch_depth/2, -block_height/2 + notch_height/2) * Box(notch_width, notch_depth, notch_height)
solid_body = solid_body - notch

for i in range(2):
    for j in range(2):
        x = (i - 0.5) * hole_spacing_x
        y = (j - 0.5) * hole_spacing_y
        hole = Pos(x, y, 0) * Cylinder(hole_diameter/2, block_height * 2)
        solid_body = solid_body - hole

part = solid_body
part.name = "block_with_pocket_notch_holes"
export_step(part, "output.step")