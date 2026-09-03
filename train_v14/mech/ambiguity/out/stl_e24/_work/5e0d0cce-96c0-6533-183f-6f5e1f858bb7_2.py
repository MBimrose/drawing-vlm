from build123d import *

block_length = 80.0
block_width = 40.0
block_height = 20.0
slot_width = 10.0
slot_length = 30.0
slot_offset = 5.0
boss_diameter = 12.0
boss_height = 8.0
boss_offset = 5.0
fillet_radius = 0.5
chamfer_distance = 1.0
mount_hole_dia = 5.0
mount_hole_offset = 5.0

solid = Box(block_width, block_length, block_height)
solid = solid - Pos(0, slot_offset, 0) * Box(slot_width, slot_length, block_height)
solid = solid + Pos(0, -block_length/2 + boss_offset + boss_diameter/2, block_height - boss_height) * Cylinder(boss_diameter/2, boss_height)

hole_positions = [
    (-block_width/2 + mount_hole_offset + mount_hole_dia/2, -block_length/2 + mount_hole_offset + mount_hole_dia/2),
    ( block_width/2 - mount_hole_offset - mount_hole_dia/2, -block_length/2 + mount_hole_offset + mount_hole_dia/2),
    (-block_width/2 + mount_hole_offset + mount_hole_dia/2,  block_length/2 - mount_hole_offset - mount_hole_dia/2),
    ( block_width/2 - mount_hole_offset - mount_hole_dia/2,  block_length/2 - mount_hole_offset - mount_hole_dia/2),
]
for x, y in hole_positions:
    solid = solid - Pos(x, y, 0) * Cylinder(mount_hole_dia/2, block_height)

solid = chamfer(solid.edges().filter_by(Axis.Z), chamfer_distance)
solid = fillet(solid.edges().filter_by(Axis.Z), fillet_radius)

part = solid
part.name = "block_with_slot_boss_and_holes"
export_step(part, "output.step")