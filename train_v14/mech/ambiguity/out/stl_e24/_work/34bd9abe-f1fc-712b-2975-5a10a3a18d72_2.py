from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 20.0
channel_width = 10.0
channel_depth = 10.0
pocket_width = 20.0
pocket_depth = 5.0
fillet_radius = 1.0
mount_hole_dia = 5.0
mount_hole_spacing = 30.0
mount_hole_offset = 10.0

solid_body = Pos(0, 0, block_height/2) * Box(block_length, block_width, block_height)

channel = Pos(0, 0, block_height - channel_depth/2) * Box(channel_width, block_length, channel_depth)
solid_body = solid_body - channel

pocket = Pos(0, 0, block_height - pocket_depth/2) * Box(pocket_width, block_width, pocket_depth)
solid_body = solid_body - pocket

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = fillet(bottom_face.edges(), fillet_radius)

for y in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    hole = Pos(0, y, block_height/2) * Rot(0, 90, 0) * Cylinder(mount_hole_dia/2, block_length)
    solid_body = solid_body - hole

part = solid_body
part.name = "block_with_channel_pocket_and_holes"
export_step(part, "output.step")