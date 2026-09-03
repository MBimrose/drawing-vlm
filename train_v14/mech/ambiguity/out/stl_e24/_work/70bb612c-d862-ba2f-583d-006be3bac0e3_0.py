from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 30.0
boss_diameter = 20.0
boss_height = 15.0
hole_diameter = 4.0
hole_spacing_x = 60.0
hole_spacing_y = 40.0
fillet_radius = 2.0

base = Box(block_length, block_width, block_height)
boss = Cylinder(boss_diameter / 2, boss_height)
solid_body = base + boss
solid_body = fillet(solid_body.edges(), fillet_radius)

hole_r = hole_diameter / 2
hole_h = block_height + boss_height + 10
for x in [-hole_spacing_x/2, hole_spacing_x/2]:
    for y in [-hole_spacing_y/2, hole_spacing_y/2]:
        solid_body = solid_body - Pos(x, y, block_height/2) * Rot(90, 0, 0) * Cylinder(hole_r, hole_h)

part = solid_body
part.name = "block_with_boss_and_holes"
export_step(part, "output.step")