from build123d import *

channel_length = 80.0
channel_width = 40.0
channel_height = 15.0
wall_thickness = 2.0
rib_width = 6.0
rib_height = 8.0
fillet_radius = 0.5
chamfer_distance = 0.5
hole_diameter = 3.0
hole_offset = 20.0
slot_width = 4.0
slot_height = 6.0
slot_offset = 30.0

base = Box(channel_width, channel_height, channel_length)
inner = Pos(0, wall_thickness / 2, 0) * Box(channel_width - 2 * wall_thickness, channel_height - wall_thickness, channel_length)
channel = base - inner

rib = Pos(0, wall_thickness / 2, 0) * Box(rib_width, rib_height, channel_length)
channel = channel + rib

channel = chamfer(channel.edges().filter_by(Axis.Z), chamfer_distance)
channel = fillet(channel.edges(), fillet_radius)

hole = Pos(channel_width / 2, 0, hole_offset) * Rot(0, 90, 0) * Cylinder(hole_diameter / 2, channel_width)
channel = channel - hole

slot = Pos(0, channel_height / 2, slot_offset) * Box(slot_width, slot_height, wall_thickness * 2)
channel = channel - slot

part = channel
part.name = "channel_with_rib"
export_step(part, "output.step")