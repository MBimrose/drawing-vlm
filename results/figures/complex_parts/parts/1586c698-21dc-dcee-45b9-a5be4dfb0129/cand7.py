from build123d import *

channel_length = 90.0
channel_width = 30.0
channel_height = 20.0
wall_thickness = 2.0
notch_width = 10.0
notch_depth = 8.0
hole_diameter = 5.0
hole_offset_from_end = 12.0
rib_thickness = 1.0
rib_height = channel_height - 2 * wall_thickness

base = Pos(0, 0, channel_height/2) * Box(channel_length, channel_width, channel_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

notch = Pos(channel_length/2 - notch_width/2, 0, channel_height - notch_depth/2) * Box(notch_width, notch_depth, notch_depth)
base = base - notch

for x, y in [(-channel_length/2 + hole_offset_from_end, 0), (channel_length/2 - hole_offset_from_end, 0)]:
    base = base - Pos(x, y, channel_height/2) * Cylinder(hole_diameter/2, channel_height)

rib = Pos(0, 0, wall_thickness + rib_height/2) * Box(rib_thickness, channel_length, rib_height)
base = base + rib

ext_rib = Pos(0, channel_width/2 + rib_thickness/2, wall_thickness + rib_height/2) * Box(rib_thickness, channel_length, rib_height)
base = base + ext_rib

part = base
part.name = "channel_with_ribs"
export_step(part, "output.step")