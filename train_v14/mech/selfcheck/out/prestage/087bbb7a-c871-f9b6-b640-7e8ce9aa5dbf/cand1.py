from build123d import *

channel_length = 100.0
channel_width = 30.0
channel_height = 20.0
wall_thickness = 2.0
slot_width = 6.0
slot_depth = channel_width - 2 * wall_thickness
fillet_radius = 1.0
hole_diameter = 4.0
hole_spacing = 15.0
hole_count = 4
rib_width = 10.0
rib_height = 4.0

base = Box(channel_length, channel_width, channel_height)
inner_cut = Box(channel_length, channel_width - 2 * wall_thickness, channel_height - 2 * wall_thickness)
channel = base - inner_cut

slot = Box(channel_length, slot_width, slot_depth)
channel = channel - slot

x_edges = channel.edges().filter_by(Axis.X)
channel = fillet(x_edges, fillet_radius)

for i in range(hole_count):
    x = (i - (hole_count - 1) / 2) * hole_spacing
    hole = Pos(x, channel_width / 2, 0) * Rot(90, 0, 0) * Cylinder(hole_diameter / 2, channel_width + 10)
    channel = channel - hole

rib = Pos(0, 0, channel_height / 2 - rib_height / 2) * Box(channel_length, rib_width, rib_height)
channel = channel + rib

part = channel
part.name = "channel_with_rib"
export_step(part, "output.step")