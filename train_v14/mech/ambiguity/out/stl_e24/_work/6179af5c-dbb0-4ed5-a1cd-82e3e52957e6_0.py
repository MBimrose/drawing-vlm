from build123d import *

channel_length = 80.0
channel_width = 40.0
channel_height = 15.0
wall_thickness = 2.0
rib_height = 10.0
rib_thickness = 2.0
hole_diameter = 3.0
hole_offset_from_end = 20.0
chamfer_size = 0.5
fillet_radius = 0.5

outer = Box(channel_width, channel_height, channel_length)
inner = Pos(0, wall_thickness / 2, 0) * Box(channel_width - 2 * wall_thickness, channel_height - wall_thickness, channel_length)
channel = outer - inner

rib = Pos(0, -channel_height / 2 + wall_thickness + rib_height / 2, 0) * Box(rib_thickness, rib_height, channel_length)
channel = channel + rib

hole_r = hole_diameter / 2
hole_h = channel_width + 20
hole_z = hole_offset_from_end
channel = channel - Pos(channel_width / 2, 0, hole_z) * Rot(0, 90, 0) * Cylinder(hole_r, hole_h)
channel = channel - Pos(-channel_width / 2, 0, hole_z) * Rot(0, 90, 0) * Cylinder(hole_r, hole_h)

channel = chamfer(channel.edges().filter_by(Axis.Z), chamfer_size)
channel = fillet(channel.edges(), fillet_radius)

part = channel
part.name = "channel_with_rib_and_holes"
export_step(part, "output.step")