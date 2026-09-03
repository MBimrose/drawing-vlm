from build123d import *

channel_length = 80.0
channel_width = 40.0
channel_height = 30.0
wall_thickness = 2.0
notch_width = 8.0
notch_height = 6.0
chamfer_distance = 0.5
hole_diameter = 5.0
hole_spacing = 30.0

solid_body = Box(channel_width, channel_height, channel_length)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

notch = Pos(-channel_width/2 + wall_thickness + notch_width/2,
            channel_height/2 - wall_thickness - notch_height/2,
            -channel_length/2 + wall_thickness) * Box(notch_width, notch_height, wall_thickness * 2)
solid_body = solid_body - notch

x_face = solid_body.faces().sort_by(Axis.X)[-1]
solid_body = chamfer(x_face.edges(), chamfer_distance)

for x in [-hole_spacing/2, hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(hole_diameter/2, channel_length)

part = solid_body
part.name = "channel_with_notch_and_holes"
export_step(part, "output.step")