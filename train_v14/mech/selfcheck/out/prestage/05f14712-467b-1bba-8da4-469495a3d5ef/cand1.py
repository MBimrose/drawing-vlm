from build123d import *

block_width = 70.0
block_depth = 50.0
block_height = 30.0
hole_diameter = 12.0
hole_spacing = 30.0
fillet_radius = 1.0
chamfer_distance = 1.0
mount_hole_diameter = 4.0
mount_hole_offset = 10.0
side_hole_diameter = 6.0
side_hole_offset = 5.0
pocket_width = 20.0
pocket_depth = 30.0
pocket_height = 8.0
pocket_offset_x = -15.0
slot_width = 5.0
slot_length = 60.0
slot_depth = 3.0

solid = Box(block_width, block_depth, block_height)

for x in [-hole_spacing/2, hole_spacing/2]:
    solid = solid - Pos(x, 0, 0) * Cylinder(hole_diameter/2, block_height)

solid = fillet(solid.edges().filter_by(Axis.Z), fillet_radius)

top_face = solid.faces().sort_by(Axis.Z)[-1]
solid = chamfer(top_face.edges(), chamfer_distance)

mount_pts = [
    (-block_width/2 + mount_hole_offset, -block_depth/2 + mount_hole_offset),
    ( block_width/2 - mount_hole_offset, -block_depth/2 + mount_hole_offset),
    (-block_width/2 + mount_hole_offset,  block_depth/2 - mount_hole_offset),
    ( block_width/2 - mount_hole_offset,  block_depth/2 - mount_hole_offset)
]
for x, y in mount_pts:
    solid = solid - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, block_height)

solid = solid - Pos(0, 0, block_height/2 - side_hole_offset) * Rot(0, 90, 0) * Cylinder(side_hole_diameter/2, block_width)

solid = solid - Pos(pocket_offset_x, 0, -block_height/2 + pocket_height/2) * Box(pocket_width, pocket_depth, pocket_height)

solid = solid - Pos(0, 0, block_height/2 - slot_depth/2) * Box(slot_length, slot_width, slot_depth)

part = solid
part.name = "block_with_holes_and_pockets"
export_step(part, "output.step")