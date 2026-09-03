from build123d import *

channel_length = 80.0
channel_width = 40.0
channel_height = 15.0
wall_thickness = 2.0
rib_width = 4.0
rib_height = 10.0
fillet_radius = 0.5
chamfer_distance = 0.5
hole_diameter = 3.0
hole_offset_from_end = 20.0

outer = Pos(0, 0, channel_length/2) * Box(channel_width, channel_height, channel_length)
inner = Pos(0, wall_thickness/2, channel_length/2) * Box(channel_width - 2*wall_thickness, channel_height - wall_thickness, channel_length)
channel = outer - inner

rib = Pos(0, wall_thickness/2, channel_length/2) * Box(rib_width, rib_height, channel_length)
channel = channel + rib

channel = chamfer(channel.edges().filter_by(Axis.Z), chamfer_distance)
channel = fillet(channel.edges(), fillet_radius)

hole_r = hole_diameter / 2
hole_cyl = Rot(0, 90, 0) * Cylinder(hole_r, channel_length)
channel = channel - Pos(channel_width/2, 0, channel_length/2 + hole_offset_from_end) * hole_cyl
channel = channel - Pos(-channel_width/2, 0, channel_length/2 + hole_offset_from_end) * hole_cyl

part = channel
part.name = "channel_with_rib"
export_step(part, "output.step")