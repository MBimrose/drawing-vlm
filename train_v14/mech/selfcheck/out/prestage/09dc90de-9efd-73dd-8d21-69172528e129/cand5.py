from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 30.0
wall_thickness = 4.0
fillet_radius = 2.0
boss_diameter = 12.0
boss_height = 8.0
hole_diameter = 5.0
hole_spacing_x = 12.0
hole_spacing_y = 12.0
hole_rows = 3
hole_cols = 4

base = Box(block_width, block_length, block_height)
base = fillet(base.edges(), fillet_radius)

boss = Pos(0, 0, block_height/2 - boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid_body = base + boss

cavity = Pos(0, 0, wall_thickness/2) * Box(block_width - 2*wall_thickness, block_length - 2*wall_thickness, block_height - wall_thickness)
solid_body = solid_body - cavity

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        hole = Pos(x, y, 0) * Cylinder(hole_diameter/2, block_height + 10)
        solid_body = solid_body - hole

part = solid_body
part.name = "hollow_block_with_boss_and_holes"
export_step(part, "output.step")