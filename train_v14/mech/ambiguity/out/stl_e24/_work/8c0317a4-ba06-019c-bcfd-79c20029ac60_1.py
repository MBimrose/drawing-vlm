from build123d import *

channel_length = 80.0
channel_width = 40.0
channel_height = 30.0
wall_thickness = 2.5
rib_width = 6.0
rib_height = 4.0
rib_spacing = 15.0
fillet_radius = 1.2
mount_hole_dia = 4.0
mount_hole_offset = 20.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 12.0

solid_body = Pos(0, 0, channel_height/2) * Box(channel_length, channel_width, channel_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

rib_count = int((channel_length - 2 * wall_thickness) // rib_spacing)
for i in range(rib_count):
    x = (i - (rib_count - 1) / 2) * rib_spacing
    solid_body = solid_body + Pos(x, 0, wall_thickness) * Box(rib_width, rib_height, wall_thickness * 2)

for x in [-mount_hole_offset, mount_hole_offset]:
    solid_body = solid_body - Pos(x, 0, channel_height/2) * Cylinder(mount_hole_dia/2, channel_height + 10)

solid_body = solid_body - Pos(0, 0, pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)

part = solid_body
part.name = "channel_with_ribs"
export_step(part, "output.step")