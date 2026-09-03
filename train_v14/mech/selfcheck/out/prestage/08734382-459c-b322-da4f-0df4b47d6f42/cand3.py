from build123d import *

channel_width = 80.0
channel_height = 60.0
wall_thickness = 8.0
length = 80.0
fillet_radius = 2.0
rib_width = 6.0
rib_height = 4.0
rib_spacing = 12.0
hole_diameter = 4.0
hole_spacing = 30.0

outer = Box(channel_width, channel_height, length)
inner = Pos(0, wall_thickness/2, 0) * Box(channel_width - 2*wall_thickness, channel_height - wall_thickness, length)
channel = outer - inner
channel = fillet(channel.edges(), fillet_radius)

rib1 = Pos(-rib_spacing/2, 0, -length/2 + rib_height/2) * Box(rib_width, channel_width - 2*wall_thickness, rib_height)
rib2 = Pos(rib_spacing/2, 0, -length/2 + rib_height/2) * Box(rib_width, channel_width - 2*wall_thickness, rib_height)
channel = channel + rib1 + rib2

hole1 = Pos(-hole_spacing/2, channel_height/2, 0) * Cylinder(hole_diameter/2, channel_height + 20)
hole2 = Pos(hole_spacing/2, channel_height/2, 0) * Cylinder(hole_diameter/2, channel_height + 20)
channel = channel - hole1 - hole2

part = channel
part.name = "channel_with_ribs_and_holes"
export_step(part, "output.step")