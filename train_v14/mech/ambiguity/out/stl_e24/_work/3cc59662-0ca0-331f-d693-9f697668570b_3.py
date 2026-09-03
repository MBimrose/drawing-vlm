from build123d import *

block_length = 60.0
block_width = 40.0
block_height = 20.0
bore_diameter = 20.0
boss_diameter = 24.0
boss_height = 5.0
fillet_radius = 2.0
mount_hole_diameter = 6.0
mount_hole_offset = 15.0
pocket_width = 15.0
pocket_length = 20.0
pocket_depth = 5.0

result = Box(block_length, block_width, block_height)
result = result - Cylinder(bore_diameter / 2, block_height)
result = result + Pos(0, 0, block_height / 2 + boss_height / 2) * Cylinder(boss_diameter / 2, boss_height)
result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

mount_points = [
    (-block_length / 2 + mount_hole_offset, -block_width / 2 + mount_hole_offset),
    (block_length / 2 - mount_hole_offset, -block_width / 2 + mount_hole_offset),
    (-block_length / 2 + mount_hole_offset, block_width / 2 - mount_hole_offset),
    (block_length / 2 - mount_hole_offset, block_width / 2 - mount_hole_offset),
]
for x, y in mount_points:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_diameter / 2, block_height)

result = result - Pos(0, block_width / 2 - pocket_depth / 2, 0) * Box(pocket_width, pocket_depth, pocket_length)

part = result
part.name = "block_with_boss_and_pocket"
export_step(part, "output.step")