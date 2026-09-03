from build123d import *

block_length = 80.0
block_width = 80.0
block_height = 20.0
fillet_radius = 2.0
notch_width = 10.0
notch_depth = 15.0
hole_diameter = 4.5
hole_rows = 2
hole_cols = 4
hole_spacing_x = 20.0
hole_spacing_y = 60.0
boss_radius = 8.0
boss_height = 5.0

solid_body = Box(block_length, block_width, block_height)
solid_body = fillet(solid_body.edges(), fillet_radius)

notch = Pos(0, block_width/2 - notch_depth/2, 0) * Box(notch_width, notch_depth, block_height)
solid_body = solid_body - notch

boss = Pos(0, 0, -block_height/2) * Cylinder(boss_radius, boss_height)
solid_body = solid_body + boss

start_x = -((hole_cols - 1) * hole_spacing_x) / 2
start_y = -((hole_rows - 1) * hole_spacing_y) / 2
for i in range(hole_cols):
    for j in range(hole_rows):
        x = start_x + i * hole_spacing_x
        y = start_y + j * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, block_height + 1)

part = solid_body
part.name = "notched_block_with_boss_and_holes"
export_step(part, "output.step")