from build123d import *

channel_length = 80.0
channel_width = 30.0
channel_height = 40.0
wall_thickness = 2.0
notch_width = 10.0
notch_depth = 6.0
notch_offset = 15.0
hole_diameter = 6.0
hole_spacing = 20.0
chamfer_size = 0.5

base = Pos(0, 0, channel_height/2) * Box(channel_length, channel_width, channel_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

notch1 = Pos(notch_offset, channel_width/2 - notch_depth/2, channel_height - notch_depth/2) * Box(notch_width, notch_depth, notch_depth)
notch2 = Pos(-notch_offset, -channel_width/2 + notch_depth/2, channel_height - notch_depth/2) * Box(notch_width, notch_depth, notch_depth)
base = base - notch1 - notch2

for x in [-hole_spacing/2, hole_spacing/2]:
    base = base - Pos(x, 0, channel_height/2) * Cylinder(hole_diameter/2, channel_width)

front_face = base.faces().sort_by(Axis.X)[-1]
base = chamfer(front_face.edges(), chamfer_size)
back_face = base.faces().sort_by(Axis.X)[0]
base = chamfer(back_face.edges(), chamfer_size)

part = base
part.name = "channel_with_notches_and_holes"
export_step(part, "output.step")