from build123d import *

channel_length = 80.0
channel_width = 60.0
channel_height = 40.0
wall_thickness = 4.0
mount_hole_diameter = 4.0
mount_hole_spacing = 20.0
mount_hole_offset = 10.0

outer = Pos(0, 0, channel_length/2) * Box(channel_width, channel_height, channel_length)
inner = Pos(0, 0, channel_length/2) * Box(channel_width - 2*wall_thickness, channel_height - 2*wall_thickness, channel_length - 2*wall_thickness)
solid_body = outer - inner

hole_count = int((channel_length - 2*mount_hole_offset) // mount_hole_spacing) + 1
for i in range(hole_count):
    y_pos = -channel_length/2 + mount_hole_offset + i * mount_hole_spacing
    hole = Pos(0, y_pos, wall_thickness) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, channel_width)
    solid_body = solid_body - hole

part = solid_body
part.name = "channel_with_mounting_holes"
export_step(part, "output.step")