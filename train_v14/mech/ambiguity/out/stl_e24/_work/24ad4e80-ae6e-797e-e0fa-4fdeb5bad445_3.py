from build123d import *

channel_length = 100.0
channel_width = 30.0
channel_height = 20.0
wall_thickness = 3.0
rib_height = 5.0
rib_width = 10.0
rib_length = channel_length - 20.0
fillet_radius = 2.0
hole_diameter = 5.0
hole_offset_from_end = 8.0

base = Pos(0, 0, channel_height/2) * Box(channel_length, channel_width, channel_height)
base = fillet(base.edges(), fillet_radius)

top_face = base.faces().sort_by(Axis.Z)[-1]
bottom_face = base.faces().sort_by(Axis.Z)[0]
base = offset(base, amount=-wall_thickness, openings=[top_face, bottom_face])

rib = Pos(0, -channel_width/2 + wall_thickness + rib_width/2, rib_height/2) * Box(rib_length, rib_width, rib_height)
base = base + rib

hole_x = channel_length/2 - wall_thickness/2
hole_y = -channel_length/2 + hole_offset_from_end
hole = Pos(hole_x, hole_y, channel_height/2) * Cylinder(hole_diameter/2, channel_height)
base = base - hole

part = base
part.name = "channel_with_rib"
export_step(part, "output.step")