from build123d import *

channel_length = 90.0
channel_width = 30.0
channel_height = 20.0
wall_thickness = 2.0
notch_width = 20.0
notch_height = 10.0
notch_depth = 12.0
hole_diameter = 5.0
hole_offset = 15.0
rib_thickness = 1.0
rib_height = channel_height - 2 * wall_thickness

solid_body = Pos(0, 0, channel_height/2) * Box(channel_length, channel_width, channel_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

notch = Pos(0, channel_width/2 + notch_depth/2, channel_height/2) * Box(notch_width, notch_depth, notch_height)
solid_body = solid_body - notch

for x, y in [(-channel_length/2 + hole_offset, -channel_width/2 + hole_offset),
             (channel_length/2 - hole_offset, channel_width/2 - hole_offset)]:
    solid_body = solid_body - Pos(x, y, channel_height/2) * Cylinder(hole_diameter/2, channel_height)

rib = Pos(0, 0, wall_thickness + rib_height/2) * Box(rib_thickness, channel_length, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "channel_with_notch_holes_and_rib"
export_step(part, "output.step")