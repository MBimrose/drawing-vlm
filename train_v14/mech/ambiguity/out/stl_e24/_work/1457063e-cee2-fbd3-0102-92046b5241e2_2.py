from build123d import *

channel_length = 100.0
channel_width = 60.0
channel_height = 30.0
wall_thickness = 2.0
notch_width = 20.0
notch_depth = 10.0
hole_diameter = 5.0
hole_count = 6
chamfer_distance = 0.8

solid_body = Pos(0, 0, channel_height/2) * Box(channel_length, channel_width, channel_height)

notch = Pos(-channel_length/2 + notch_depth/2, 0, channel_height/2) * Box(notch_depth, notch_width, channel_height)
solid_body = solid_body - notch

solid_body = offset(solid_body, amount=-wall_thickness)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[bottom_face])

x_face = solid_body.faces().sort_by(Axis.X)[0]
solid_body = chamfer(x_face.edges(), chamfer_distance)

hole_spacing = channel_length / (hole_count + 1)
for i in range(hole_count):
    x = -channel_length/2 + hole_spacing * (i + 1)
    solid_body = solid_body - Pos(x, 0, channel_height/2) * Cylinder(hole_diameter/2, channel_height + 10)

part = solid_body
part.name = "channel_with_notch_and_holes"
export_step(part, "output.step")