from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 30.0
rib_height = 8.0
rib_width = 12.0
rib_length = block_length
hole_diameter = 4.0
hole_offset = 6.0
fillet_radius = 2.0
pocket_depth = 5.0
pocket_width = 20.0
pocket_length = 40.0

solid_body = Box(block_length, block_width, block_height)
solid_body = fillet(solid_body.edges(), fillet_radius)

rib = Pos(0, 0, block_height/2 - rib_height/2) * Box(rib_length, rib_width, rib_height)
solid_body = solid_body + rib

hole_r = hole_diameter / 2
hole_cyl = Rot(90, 0, 0) * Cylinder(hole_r, block_width + 10)
for x in [-(block_length/2 - hole_offset), block_length/2 - hole_offset]:
    for z in [block_height/2, -block_height/2]:
        solid_body = solid_body - Pos(x, 0, z) * hole_cyl

pocket = Pos(0, 0, block_height/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

part = solid_body
part.name = "block_with_rib_holes_pocket"
export_step(part, "output.step")