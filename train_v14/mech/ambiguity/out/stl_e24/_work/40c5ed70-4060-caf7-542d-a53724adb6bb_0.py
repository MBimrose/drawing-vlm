from build123d import *

chute_length = 80.0
chute_width = 50.0
chute_height = 30.0
wall_thickness = 3.0
channel_width = 20.0
channel_depth = 5.0
chamfer_size = 2.0
mount_hole_dia = 4.0
mount_hole_spacing = 30.0

solid_body = Pos(0, 0, chute_height/2) * Box(chute_length, chute_width, chute_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

channel = Pos(0, 0, chute_height - wall_thickness - channel_depth/2) * Box(chute_length - 2*wall_thickness, channel_width, channel_depth)
solid_body = solid_body - channel

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

for y in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid_body = solid_body - Pos(-chute_length/2, y, chute_height/2) * Rot(0, 90, 0) * Cylinder(mount_hole_dia/2, chute_length)
    solid_body = solid_body - Pos(chute_length/2, y, chute_height/2) * Rot(0, 90, 0) * Cylinder(mount_hole_dia/2, chute_length)

part = solid_body
part.name = "chute"
export_step(part, "output.step")