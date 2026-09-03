from build123d import *

block_width = 60.0
block_depth = 40.0
block_height = 20.0
fillet_radius = 2.0
hole_diameter = 6.0
hole_spacing_x = 30.0
hole_spacing_y = 20.0
hole_rows = 2
hole_cols = 2
rib_thickness = 4.0
rib_height = 5.0
pocket_width = 25.0
pocket_depth = 15.0
pocket_height = 6.0
pocket_offset_x = 10.0
pocket_offset_y = 10.0

solid_body = Box(block_width, block_depth, block_height)
solid_body = fillet(solid_body.edges(), fillet_radius)

rib = Pos(0, 0, block_height/2 - rib_height/2) * Box(rib_thickness, block_depth - 2*fillet_radius, rib_height)
solid_body = solid_body + rib

pocket = Pos(-block_width/2 + pocket_offset_x, -block_depth/2 + pocket_offset_y, -block_height/2 + pocket_height/2) * Box(pocket_width, pocket_depth, pocket_height)
solid_body = solid_body - pocket

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        hole = Pos(x, y, 0) * Cylinder(hole_diameter/2, block_height * 2)
        solid_body = solid_body - hole

part = solid_body
part.name = "block_with_rib_pocket_holes"
export_step(part, "output.step")