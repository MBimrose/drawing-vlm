from build123d import *

channel_length = 80.0
channel_width = 40.0
channel_height = 30.0
wall_thickness = 2.0
notch_width = 6.0
notch_depth = 4.0
notch_offset_from_side = 5.0
chamfer_size = 0.5
hole_diameter = 5.0
hole_spacing = 30.0

base = Pos(0, 0, channel_length/2) * Box(channel_width, channel_height, channel_length)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

notch_x = -channel_width/2 + notch_offset_from_side + notch_width/2
notch_y = channel_height/2 - wall_thickness - notch_depth/2
notch = Pos(notch_x, notch_y, notch_depth/2) * Box(notch_width, notch_depth, notch_depth)
base = base - notch

x_face = base.faces().sort_by(Axis.X)[-1]
base = chamfer(x_face.edges(), chamfer_size)

for x in [-hole_spacing/2, hole_spacing/2]:
    base = base - Pos(x, 0, channel_length/2) * Cylinder(hole_diameter/2, channel_length + 10)

part = base
part.name = "channel_with_notch_and_holes"
export_step(part, "output.step")