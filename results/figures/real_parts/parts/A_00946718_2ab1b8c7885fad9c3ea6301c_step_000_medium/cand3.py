from build123d import *

block_length = 80.0
block_width = 30.0
block_thickness = 15.0
cyl_radius = 20.0
cyl_height = block_thickness
hole_diameter = 15.0
hole_spacing = 55.0
fillet_radius = 2.0
pocket_width = 12.0
pocket_depth = 8.0
pocket_offset = 25.0

base = Box(block_length, block_width, block_thickness)
cyl = Cylinder(cyl_radius, cyl_height)
solid_body = base + cyl

solid_body = solid_body - Cylinder(hole_diameter/2, block_thickness * 2)
for x in [-hole_spacing/2, hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(hole_diameter/2, block_thickness * 2)

pocket = Pos(pocket_offset, 0, block_thickness - pocket_depth/2) * Box(pocket_width, pocket_depth, pocket_depth)
solid_body = solid_body - pocket

solid_body = fillet(solid_body.edges(), fillet_radius)

part = solid_body
part.name = "block_with_cylinder_holes_pocket"
export_step(part, "output.step")