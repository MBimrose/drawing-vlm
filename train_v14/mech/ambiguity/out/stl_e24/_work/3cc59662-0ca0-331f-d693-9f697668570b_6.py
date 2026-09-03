from build123d import *

block_length = 60.0
block_width = 40.0
block_height = 20.0
central_hole_dia = 20.0
slot_length = 20.0
slot_width = 15.0
slot_depth = 5.0
slot_offset = 10.0
mount_hole_dia = 6.0
mount_hole_spacing = 30.0
fillet_radius = 2.0
boss_radius = 12.0
boss_height = 5.0

solid_body = Box(block_length, block_width, block_height)
solid_body = solid_body - Cylinder(central_hole_dia/2, block_height + boss_height + 10)
solid_body = solid_body - Pos(0, block_width/2 - slot_depth/2, slot_offset) * Box(slot_length, slot_depth, slot_width)

for i in range(2):
    for j in range(2):
        x = (i - 0.5) * mount_hole_spacing
        y = (j - 0.5) * mount_hole_spacing
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_dia/2, block_height + boss_height + 10)

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)
solid_body = solid_body + Pos(0, 0, block_height/2 + boss_height/2) * Cylinder(boss_radius, boss_height)

part = solid_body
part.name = "block_with_holes_and_boss"
export_step(part, "output.step")