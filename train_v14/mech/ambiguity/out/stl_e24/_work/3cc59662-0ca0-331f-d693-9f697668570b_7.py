from build123d import *

block_length = 60.0
block_width = 40.0
block_height = 20.0
central_hole_dia = 20.0
boss_dia = 24.0
boss_height = 5.0
mount_hole_dia = 6.0
mount_hole_offset = 15.0
fillet_radius = 2.0
pocket_width = 15.0
pocket_length = 20.0
pocket_depth = 5.0

base = Box(block_length, block_width, block_height)
base = base - Cylinder(central_hole_dia/2, block_height + 10)

boss = Pos(0, 0, block_height/2 + boss_height/2) * Cylinder(boss_dia/2, boss_height)
base = base + boss

for x, y in [(mount_hole_offset, mount_hole_offset), (-mount_hole_offset, mount_hole_offset),
             (mount_hole_offset, -mount_hole_offset), (-mount_hole_offset, -mount_hole_offset)]:
    base = base - Pos(x, y, 0) * Cylinder(mount_hole_dia/2, block_height + 10)

base = fillet(base.edges().filter_by(Axis.Z), fillet_radius)

pocket = Pos(0, block_width/2 - pocket_depth/2, 0) * Box(pocket_width, pocket_depth, pocket_length)
base = base - pocket

part = base
part.name = "block_with_boss_and_pocket"
export_step(part, "output.step")