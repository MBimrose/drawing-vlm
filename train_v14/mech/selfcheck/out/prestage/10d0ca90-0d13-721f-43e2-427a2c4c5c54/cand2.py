from build123d import *

channel_length = 80.0
channel_width = 40.0
channel_height = 30.0
wall_thickness = 2.0
notch_width = 6.0
notch_height = 8.0
notch_depth = 4.0
notch_offset_from_end = 5.0
chamfer_size = 0.5
hole_diameter = 5.0
hole_spacing = 30.0

solid_body = Box(channel_width, channel_height, channel_length)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

notch_x = -channel_width/2 + notch_offset_from_end + notch_width/2
notch_y = channel_height/2 - notch_height/2 - wall_thickness
notch_z = -channel_length/2 + wall_thickness + notch_depth/2
notch_box = Pos(notch_x, notch_y, notch_z) * Box(notch_width, notch_height, notch_depth)
solid_body = solid_body - notch_box

for x in [-hole_spacing/2, hole_spacing/2]:
    hole = Pos(x, 0, 0) * Cylinder(hole_diameter/2, channel_length + 10)
    solid_body = solid_body - hole

x_face = solid_body.faces().sort_by(Axis.X)[-1]
x_edges = x_face.edges()
solid_body = chamfer(x_edges, chamfer_size)

part = solid_body
part.name = "channel_with_notch_and_holes"
export_step(part, "output.step")