from build123d import *

channel_length = 100.0
channel_width = 30.0
channel_height = 20.0
wall_thickness = 3.0
rib_height = 8.0
rib_width = 10.0
rib_length = 80.0
rib_offset = 10.0
hole_diameter = 5.0
hole_spacing = 20.0
hole_count = 4
hole_offset_from_edge = 12.0
fillet_radius = 2.0

outer = Pos(0, 0, channel_height / 2) * Box(channel_length, channel_width, channel_height)
outer = fillet(outer.edges(), fillet_radius)

inner = Pos(0, 0, channel_height / 2) * Box(channel_length - 2 * wall_thickness, channel_width - 2 * wall_thickness, channel_height)
channel = outer - inner

rib = Pos(-channel_length / 2 + rib_offset + rib_length / 2, -channel_width / 2 + wall_thickness + rib_width / 2, rib_height / 2) * Box(rib_length, rib_width, rib_height)
channel = channel + rib

hole_x = channel_length / 2 - wall_thickness / 2
for i in range(hole_count):
    y = -channel_width / 2 + wall_thickness + hole_offset_from_edge + i * hole_spacing
    channel = channel - Pos(hole_x, y, channel_height / 2) * Cylinder(hole_diameter / 2, channel_height)

part = channel
part.name = "channel_with_rib_and_holes"
export_step(part, "output.step")