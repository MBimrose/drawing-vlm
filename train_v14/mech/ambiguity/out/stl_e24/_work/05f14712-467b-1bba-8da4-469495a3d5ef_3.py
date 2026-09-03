from build123d import *

block_length = 70.0
block_width = 50.0
block_height = 30.0
slot_length = 60.0
slot_width = 5.0
hole_diameter = 12.0
hole_spacing = 25.0
fillet_radius = 1.0
chamfer_distance = 1.0
mount_hole_diameter = 4.0
mount_hole_offset = 10.0
rib_thickness = 3.0
rib_height = 8.0
rib_spacing = 15.0
pocket_length = 20.0
pocket_width = 30.0
pocket_depth = 10.0
boss_diameter = 10.0
boss_height = 5.0
side_hole_diameter = 6.0
side_hole_offset = 12.0

result = Box(block_length, block_width, block_height)
result = result - Box(slot_length, slot_width, block_height)

for x in [-hole_spacing/2, hole_spacing/2]:
    result = result - Pos(x, 0, 0) * Cylinder(hole_diameter/2, block_height)

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

for x, y in [(-block_length/2 + mount_hole_offset, -block_width/2 + mount_hole_offset),
             (block_length/2 - mount_hole_offset, -block_width/2 + mount_hole_offset),
             (-block_length/2 + mount_hole_offset, block_width/2 - mount_hole_offset),
             (block_length/2 - mount_hole_offset, block_width/2 - mount_hole_offset)]:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, block_height)

result = result - Pos(-block_length/4, 0, -block_height/2 + pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = result + Pos(0, 0, block_height/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
result = result - Pos(0, 0, side_hole_offset) * Rot(0, 90, 0) * Cylinder(side_hole_diameter/2, block_length)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_distance)

part = result
part.name = "block_with_features"
export_step(part, "output.step")