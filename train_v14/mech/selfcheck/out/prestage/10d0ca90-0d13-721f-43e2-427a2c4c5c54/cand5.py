from build123d import *

channel_length = 80.0
channel_width = 40.0
channel_height = 30.0
wall_thickness = 2.0
keyway_width = 6.0
keyway_depth = 4.0
keyway_offset_from_bottom = 10.0
hole_diameter = 5.0
hole_spacing = 30.0
chamfer_distance = 0.5

base = Pos(0, 0, channel_length/2) * Box(channel_width, channel_height, channel_length)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

keyway = Pos(-channel_width/2 + wall_thickness + keyway_width/2, keyway_offset_from_bottom + keyway_width/2, keyway_depth/2) * Box(keyway_width, keyway_width, keyway_depth)
base = base - keyway

for x in [-hole_spacing/2, hole_spacing/2]:
    base = base - Pos(x, 0, channel_length/2) * Cylinder(hole_diameter/2, channel_length + 10)

x_face = base.faces().sort_by(Axis.X)[-1]
base = chamfer(x_face.edges(), chamfer_distance)

part = base
part.name = "channel_with_keyway"
export_step(part, "output.step")