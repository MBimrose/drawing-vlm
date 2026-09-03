from build123d import *

block_length = 80.0
block_width = 40.0
block_height = 20.0
groove_radius = 12.0
groove_depth = 4.0
boss_radius = 10.0
boss_height = 10.0
hole_diameter = 5.0
hole_spacing = 30.0
hole_rows = 2
hole_cols = 2

result = Box(block_length, block_width, block_height)

groove = Pos(block_length/2 - groove_depth/2, 0, 0) * Rot(0, 90, 0) * Cylinder(groove_radius, groove_depth)
result = result - groove

boss = Pos(-block_length/2 + boss_height/2, 0, 0) * Rot(0, 90, 0) * Cylinder(boss_radius, boss_height)
result = result + boss

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing
        y = (j - (hole_rows - 1) / 2) * hole_spacing
        hole = Pos(x, y, 0) * Cylinder(hole_diameter / 2, block_height + 20)
        result = result - hole

part = result
part.name = "block_with_groove_boss_and_holes"
export_step(part, "output.step")