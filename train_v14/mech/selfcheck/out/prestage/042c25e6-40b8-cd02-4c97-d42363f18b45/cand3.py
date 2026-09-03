from build123d import *

block_length = 60.0
block_width = 40.0
block_height = 20.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 10.0
pocket_offset_x = 15.0
pocket_offset_y = 10.0
hole_diameter = 6.0
hole_spacing_x = 30.0
hole_spacing_y = 20.0
fillet_radius = 2.0

solid_body = Pos(0, 0, block_height / 2) * Box(block_length, block_width, block_height)
solid_body = fillet(solid_body.edges(), fillet_radius)

pocket_center_x = -block_length / 2 + pocket_offset_x
pocket_center_y = -block_width / 2 + pocket_offset_y
pocket_cut = Pos(pocket_center_x, pocket_center_y, pocket_depth / 2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket_cut

hole_radius = hole_diameter / 2
for dx in [-hole_spacing_x / 2, hole_spacing_x / 2]:
    for dy in [-hole_spacing_y / 2, hole_spacing_y / 2]:
        hole = Pos(dx, dy, block_height / 2) * Cylinder(hole_radius, block_height)
        solid_body = solid_body - hole

part = solid_body
part.name = "filleted_block_with_pocket_and_holes"
export_step(part, "output.step")