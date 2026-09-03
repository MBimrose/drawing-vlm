from build123d import *

channel_length = 80.0
channel_width = 40.0
channel_height = 30.0
wall_thickness = 2.0
pocket_width = 8.0
pocket_height = 6.0
pocket_depth = 4.0
pocket_offset_from_end = 5.0
mount_hole_diameter = 5.0
mount_hole_spacing = 30.0
rib_width = 10.0
rib_height = 4.0
rib_thickness = 2.0
chamfer_size = 0.5

solid_body = Box(channel_width, channel_height, channel_length)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

pocket_x = -channel_width/2 + pocket_offset_from_end + pocket_width/2
pocket_y = channel_height/2 - wall_thickness - pocket_height/2
pocket_z = -channel_length/2 + pocket_depth/2
solid_body = solid_body - Pos(pocket_x, pocket_y, pocket_z) * Box(pocket_width, pocket_height, pocket_depth)

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(mount_hole_diameter/2, channel_length)

rib_x = -channel_width/2 + wall_thickness + rib_width/2
rib_z = -channel_length/2 + wall_thickness + rib_thickness/2
solid_body = solid_body + Pos(rib_x, 0, rib_z) * Box(rib_width, rib_height, rib_thickness)

x_face = solid_body.faces().sort_by(Axis.X)[-1]
solid_body = chamfer(x_face.edges(), chamfer_size)

part = solid_body
part.name = "channel_with_pocket_ribs"
export_step(part, "output.step")