from build123d import *

leg_length = 50.0
leg_width = 35.0
wall_thickness = 8.0
channel_depth = 12.0
notch_radius = 6.0
fillet_radius = 2.0
hole_diameter = 4.0
hole_offset = 10.0

outer = Pos(0, 0, channel_depth/2) * Box(leg_length, leg_width, channel_depth)
inner = Pos(wall_thickness/2, wall_thickness/2, channel_depth/2) * Box(leg_length - wall_thickness, leg_width - wall_thickness, channel_depth)
channel = outer - inner

notch = Pos(leg_length/2 - wall_thickness/2, leg_width/2 - wall_thickness/2, channel_depth/2) * Cylinder(notch_radius, channel_depth)
channel = channel - notch

channel = fillet(channel.edges().filter_by(Axis.Z), fillet_radius)

hole = Pos(hole_offset, hole_offset, channel_depth/2) * Cylinder(hole_diameter/2, channel_depth)
channel = channel - hole

part = channel
part.name = "L_channel_with_notch_and_hole"
export_step(part, "output.step")