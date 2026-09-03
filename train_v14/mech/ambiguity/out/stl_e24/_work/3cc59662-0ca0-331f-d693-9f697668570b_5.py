from build123d import *

block_length = 60.0
block_width = 40.0
block_height = 20.0
central_hole_diameter = 20.0
corner_hole_diameter = 6.0
corner_hole_offset = 10.0
fillet_radius = 2.0
notch_width = 15.0
notch_height = 10.0
notch_depth = 5.0
boss_radius = 12.0
boss_height = 5.0

result = Box(block_length, block_width, block_height)
result = result - Cylinder(central_hole_diameter / 2, block_height)

for x, y in [(corner_hole_offset, corner_hole_offset), (-corner_hole_offset, corner_hole_offset),
             (-corner_hole_offset, -corner_hole_offset), (corner_hole_offset, -corner_hole_offset)]:
    result = result - Pos(x, y, 0) * Cylinder(corner_hole_diameter / 2, block_height)

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

notch = Pos(0, block_width / 2 - notch_depth / 2, 0) * Box(notch_width, notch_depth, notch_height)
result = result - notch

boss = Pos(0, 0, block_height / 2 + boss_height / 2) * Cylinder(boss_radius, boss_height)
result = result + boss

part = result
part.name = "block_with_holes_notch_and_boss"
export_step(part, "output.step")