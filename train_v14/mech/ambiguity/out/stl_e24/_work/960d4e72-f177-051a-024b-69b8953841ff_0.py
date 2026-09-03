from build123d import *

block_length = 80.0
block_width = 40.0
block_height = 20.0
boss_diameter = 20.0
boss_height = 10.0
groove_radius = 12.0
groove_depth = 4.0
hole_diameter = 5.0
hole_spacing = 30.0

base = Box(block_length, block_width, block_height)
boss = Cylinder(boss_diameter / 2, boss_height)
result = base + boss

groove = Pos(block_length / 2 - groove_depth / 2, 0, 0) * Rot(0, 90, 0) * Cylinder(groove_radius, groove_depth)
result = result - groove

for x, y in [(-hole_spacing / 2, -hole_spacing / 2), (hole_spacing / 2, -hole_spacing / 2),
             (-hole_spacing / 2, hole_spacing / 2), (hole_spacing / 2, hole_spacing / 2)]:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter / 2, block_height + boss_height + 10)

part = result
part.name = "block_with_boss_groove_and_holes"
export_step(part, "output.step")