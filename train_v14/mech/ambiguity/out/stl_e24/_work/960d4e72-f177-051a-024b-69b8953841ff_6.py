from build123d import *

block_length = 80
block_width = 40
block_height = 20
bearing_radius = 12
bearing_depth = 4
boss_radius = 6
boss_height = 10
boss_offset_x = 20
hole_diameter = 5
hole_spacing_x = 30
hole_spacing_y = 30
hole_rows = 2
hole_cols = 2
chamfer_dist = 1
fillet_radius = 2

base = Box(block_length, block_width, block_height)
boss = Pos(boss_offset_x, 0, 0) * Cylinder(boss_radius, boss_height)
result = base + boss

bearing_cut = Pos(block_length/2 - bearing_depth/2, 0, 0) * Rot(0, 90, 0) * Cylinder(bearing_radius, bearing_depth)
result = result - bearing_cut

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, block_height + boss_height + 10)

part = result
part.name = "block_with_boss_and_holes"
export_step(part, "output.step")