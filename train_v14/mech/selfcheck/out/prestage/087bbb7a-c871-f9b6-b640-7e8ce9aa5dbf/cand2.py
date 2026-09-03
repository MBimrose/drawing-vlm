from build123d import *

channel_length = 100.0
channel_width = 30.0
channel_height = 20.0
wall_thickness = 2.0
slot_width = 6.0
slot_depth = wall_thickness + 0.5
fillet_radius = 1.0
hole_diameter = 4.0
hole_spacing = 15.0
hole_count = 4
hole_offset = 10.0

outer = Box(channel_length, channel_width, channel_height)
inner = Box(channel_length, channel_width - 2*wall_thickness, channel_height - 2*wall_thickness)
solid_body = outer - inner

slot = Box(channel_length, slot_width, channel_height - 2*wall_thickness)
solid_body = solid_body - slot

solid_body = fillet(solid_body.edges().filter_by(Axis.X), fillet_radius)

for i in range(hole_count):
    x = -channel_length/2 + hole_offset + i * hole_spacing
    hole = Pos(x, channel_width/2, 0) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, channel_width + 10)
    solid_body = solid_body - hole

part = solid_body
part.name = "channel_with_slot_and_holes"
export_step(part, "output.step")