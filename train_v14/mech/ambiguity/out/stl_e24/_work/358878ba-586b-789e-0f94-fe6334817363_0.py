from build123d import *

channel_length = 80.0
channel_width = 30.0
channel_height = 40.0
wall_thickness = 2.0
notch_width = 20.0
notch_depth = 10.0
hole_diameter = 6.0
hole_spacing = 20.0
chamfer_size = 0.5

solid_body = Pos(0, 0, channel_height/2) * Box(channel_length, channel_width, channel_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

notch = Pos(0, 0, channel_height - notch_depth/2) * Box(notch_width, channel_width, notch_depth)
solid_body = solid_body - notch

for x in [-hole_spacing/2, hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, channel_height) * Cylinder(hole_diameter/2, channel_height)

front_face = solid_body.faces().sort_by(Axis.X)[-1]
solid_body = chamfer(front_face.edges(), chamfer_size)

part = solid_body
part.name = "channel_with_notch_and_holes"
export_step(part, "output.step")