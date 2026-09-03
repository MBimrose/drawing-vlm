from build123d import *

channel_length = 100.0
channel_width = 30.0
channel_height = 20.0
wall_thickness = 3.0
fillet_radius = 2.0
rib_length = 80.0
rib_width = 10.0
rib_height = 5.0
hole_diameter = 5.0
hole_offset_from_end = 8.0

base = Pos(0, 0, channel_height/2) * Box(channel_length, channel_width, channel_height)
base = fillet(base.edges(), fillet_radius)

inner = Pos(0, 0, channel_height/2) * Box(channel_length - 2*wall_thickness, channel_width - 2*wall_thickness, channel_height)
channel = base - inner

rib = Pos(0, -channel_width/2 + wall_thickness + rib_width/2, rib_height/2) * Box(rib_length, rib_width, rib_height)
channel = channel + rib

hole_center_x = channel_length/2 - wall_thickness - hole_offset_from_end
hole_center_y = -channel_width/2 + wall_thickness + rib_width/2
hole = Pos(hole_center_x, hole_center_y, channel_height/2) * Cylinder(hole_diameter/2, channel_height)
channel = channel - hole

part = channel
part.name = "channel_with_rib_and_hole"
export_step(part, "output.step")