from build123d import *

channel_length = 100.0
channel_width = 30.0
channel_height = 20.0
wall_thickness = 2.0
slot_width = 6.0
fillet_radius = 1.0
hole_diameter = 4.0
hole_spacing = 15.0
hole_offset_from_end = 15.0
rib_width = 4.0
rib_height = 6.0

base = Pos(0, 0, channel_height/2) * Box(channel_length, channel_width, channel_height)
inner = Pos(0, 0, channel_height/2) * Box(channel_length, channel_width - 2*wall_thickness, channel_height - 2*wall_thickness)
result = base - inner

slot = Pos(0, 0, channel_height/2) * Box(channel_length, slot_width, channel_height - 2*wall_thickness)
result = result - slot

x_edges = result.edges().filter_by(Axis.X)
result = fillet(x_edges, fillet_radius)

rib = Pos(0, 0, wall_thickness + rib_height/2) * Box(channel_length, rib_width, rib_height)
result = result + rib

hole_count = int((channel_length - 2 * hole_offset_from_end) // hole_spacing) + 1
for i in range(hole_count):
    x_pos = -channel_length / 2 + hole_offset_from_end + i * hole_spacing
    hole = Pos(x_pos, channel_width/2, channel_height/2) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, channel_width + 10)
    result = result - hole

part = result
part.name = "channel_with_rib_and_holes"
export_step(part, "output.step")