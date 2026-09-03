from build123d import *

block_length = 70.0
block_width = 50.0
block_height = 30.0
bearing_diameter = 12.0
bearing_spacing = 30.0
mount_hole_diameter = 4.0
mount_hole_offset = 10.0
fillet_radius = 1.0
chamfer_distance = 1.0
pocket_width = 20.0
pocket_depth = 10.0
pocket_offset = 15.0
rib_thickness = 5.0
rib_height = 6.0
rib_spacing = 15.0
slot_width = 5.0
slot_length = block_length - 10.0
slot_offset = 12.0

solid_body = Box(block_length, block_width, block_height)

for x in [-bearing_spacing/2, bearing_spacing/2]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(bearing_diameter/2, block_height)

mount_points = [
    (-block_length/2 + mount_hole_offset, -block_width/2 + mount_hole_offset),
    ( block_length/2 - mount_hole_offset, -block_width/2 + mount_hole_offset),
    (-block_length/2 + mount_hole_offset,  block_width/2 - mount_hole_offset),
    ( block_length/2 - mount_hole_offset,  block_width/2 - mount_hole_offset),
]
for x, y in mount_points:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, block_height)

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

pocket1_x = -block_length/2 + pocket_offset
pocket2_x = block_length/2 - pocket_offset
pocket_z = -block_height/2 + pocket_depth/2
solid_body = solid_body - Pos(pocket1_x, 0, pocket_z) * Box(pocket_width, block_width - 2*mount_hole_offset, pocket_depth)
solid_body = solid_body - Pos(pocket2_x, 0, pocket_z) * Box(pocket_width, block_width - 2*mount_hole_offset, pocket_depth)

rib_z = block_height/2 - rib_height/2
solid_body = solid_body + Pos(0, 0, rib_z) * Box(block_length - 2*mount_hole_offset, rib_thickness, rib_height)

slot_z = block_height/2 - slot_offset
solid_body = solid_body - Pos(0, 0, slot_z) * Rot(0, 90, 0) * Cylinder(slot_width/2, slot_length)

part = solid_body
part.name = "bearing_block"
export_step(part, "output.step")