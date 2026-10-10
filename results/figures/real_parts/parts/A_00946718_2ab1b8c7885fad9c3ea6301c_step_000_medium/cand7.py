from build123d import *

block_length = 80.0
block_width = 30.0
block_height = 20.0
cyl_radius = 25.0
cyl_height = block_height
wall_thickness = 1.5
fillet_radius = 2.7
hole_diameter = 12.0
hole_spacing = 30.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 5.0

base = Box(block_length, block_width, block_height)
cyl = Cylinder(cyl_radius, cyl_height)
solid_body = base + cyl

solid_body = offset(solid_body, amount=-wall_thickness)
solid_body = fillet(solid_body.edges(), fillet_radius)

for x, y in [(-hole_spacing, 0), (0, 0), (hole_spacing, 0)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, block_height + 10)

pocket = Pos(0, 0, block_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

part = solid_body
part.name = "shelled_block_with_holes_and_pocket"
export_step(part, "output.step")