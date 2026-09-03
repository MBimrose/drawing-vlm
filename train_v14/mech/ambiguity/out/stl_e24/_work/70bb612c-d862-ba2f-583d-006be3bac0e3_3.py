from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 30.0
wall_thickness = 4.0
rib_height = 6.0
rib_width = 4.0
rib_length = block_length - 2 * wall_thickness
fillet_radius = 2.0
hole_diameter = 4.0
hole_spacing = 20.0

solid_body = Box(block_length, block_width, block_height)
solid_body = fillet(solid_body.edges(), fillet_radius)

pocket_w = block_length - 2 * wall_thickness
pocket_d = block_width - 2 * wall_thickness
pocket_depth = block_height - wall_thickness
pocket = Pos(0, 0, block_height - pocket_depth / 2) * Box(pocket_w, pocket_d, pocket_depth)
solid_body = solid_body - pocket

rib = Pos(0, 0, rib_height / 2) * Box(rib_length, rib_width, rib_height)
solid_body = solid_body + rib

hole_r = hole_diameter / 2
hole_h = block_width + 10
for x in [-hole_spacing, hole_spacing]:
    for z in [0, block_height]:
        hole = Pos(x, 0, z) * Rot(90, 0, 0) * Cylinder(hole_r, hole_h)
        solid_body = solid_body - hole

part = solid_body
part.name = "block_with_pocket_rib_holes"
export_step(part, "output.step")