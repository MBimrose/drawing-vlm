from build123d import *

block_width = 80.0
block_depth = 60.0
block_height = 30.0
pocket_width = 40.0
pocket_depth = 30.0
pocket_height = 20.0
fillet_radius = 2.0
hole_diameter = 6.0
hole_spacing = 30.0

base = Box(block_width, block_depth, block_height)
pocket = Pos(0, 0, block_height/2 - pocket_height/2) * Box(pocket_width, pocket_depth, pocket_height)
solid_body = base - pocket

solid_body = fillet(solid_body.edges().filter_by(Axis.X), fillet_radius)

for x in [-hole_spacing/2, hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(hole_diameter/2, block_height)

part = solid_body
part.name = "XMountSocket"
export_step(part, "output.step")