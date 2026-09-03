from build123d import *

channel_length = 100.0
channel_width = 30.0
channel_height = 20.0
wall_thickness = 2.0
slot_width = 6.0
fillet_radius = 1.0
hole_diameter = 4.0
hole_spacing = 15.0
hole_count = 4
hole_offset_from_end = 15.0

base = Box(channel_length, channel_width, channel_height)
inner = Box(channel_length, channel_width - 2*wall_thickness, channel_height - 2*wall_thickness)
result = base - inner

slot = Box(channel_length, slot_width, channel_height - 2*wall_thickness)
result = result - slot

result = fillet(result.edges().filter_by(Axis.X), fillet_radius)

for i in range(hole_count):
    x = -channel_length/2 + hole_offset_from_end + i * hole_spacing
    hole = Pos(x, channel_width/2, 0) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, channel_width + 10)
    result = result - hole

part = result
part.name = "channel_with_slot_and_holes"
export_step(part, "output.step")