from build123d import *

block_width = 60.0
block_depth = 40.0
block_height = 20.0
fillet_radius = 2.0
hole_diameter = 6.0
hole_spacing_x = 30.0
hole_spacing_y = 20.0
pocket_width = 30.0
pocket_depth = 20.0
pocket_height = 10.0
pocket_offset_x = -15.0
pocket_offset_y = -10.0
boss_diameter = 12.0
boss_height = 5.0

solid_body = Pos(0, 0, block_height/2) * Box(block_width, block_depth, block_height)
solid_body = fillet(solid_body.edges(), fillet_radius)

hole_positions = [
    (-hole_spacing_x/2, -hole_spacing_y/2),
    ( hole_spacing_x/2, -hole_spacing_y/2),
    (-hole_spacing_x/2,  hole_spacing_y/2),
    ( hole_spacing_x/2,  hole_spacing_y/2),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, block_height/2) * Cylinder(hole_diameter/2, block_height + 1)

pocket = Pos(pocket_offset_x, pocket_offset_y, pocket_height/2) * Box(pocket_width, pocket_depth, pocket_height)
solid_body = solid_body - pocket

boss = Pos(0, 0, block_height - boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body + boss

part = solid_body
part.name = "block_with_holes_pocket_boss"
export_step(part, "output.step")