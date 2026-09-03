from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 30.0
groove_width = 20.0
groove_depth = 5.0
groove_length = 70.0
fillet_radius = 2.0
hole_diameter = 4.0
hole_offset = 10.0

solid_body = Box(block_length, block_width, block_height)
solid_body = fillet(solid_body.edges(), fillet_radius)

groove = Pos(0, 0, block_height - groove_depth/2) * Box(groove_length, groove_width, groove_depth)
solid_body = solid_body - groove

for x in [-block_length/2 + hole_offset, block_length/2 - hole_offset]:
    hole = Pos(x, block_width/2, block_height/2) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, block_width + 10)
    solid_body = solid_body - hole

part = solid_body
part.name = "grooved_block_with_holes"
export_step(part, "output.step")