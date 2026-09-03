from build123d import *

channel_length = 80.0
channel_width = 40.0
channel_height = 15.0
wall_thickness = 2.0
rib_thickness = 2.0
rib_height = 10.0
rib_notch_width = 5.0
rib_notch_depth = 2.0
fillet_radius = 0.5
hole_diameter = 3.0
hole_offset_from_end = 20.0
hole_offset_from_top = 5.0

base = Box(channel_width, channel_height, channel_length)
top_face = base.faces().sort_by(Axis.Y)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

rib = Pos(0, -channel_height/2 + wall_thickness + rib_height/2, 0) * Box(rib_thickness, rib_height, channel_length)
notch = Pos(rib_thickness/2 + rib_notch_depth/2, -channel_height/2 + wall_thickness + rib_height/2, 0) * Box(rib_notch_depth, rib_notch_width, channel_length)
rib = rib - notch

result = base + rib
result = fillet(result.edges(), fillet_radius)

hole = Pos(channel_width/2, 0, hole_offset_from_end) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, channel_length)
result = result - hole

part = result
part.name = "channel_with_rib"
export_step(part, "output.step")