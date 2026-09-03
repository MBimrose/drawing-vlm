from build123d import *

channel_length = 80.0
channel_width = 40.0
channel_height = 15.0
wall_thickness = 2.0
web_thickness = 2.0
fillet_radius = 0.5
chamfer_distance = 0.5
hole_diameter = 3.0
hole_spacing = 20.0
hole_count = 3
notch_width = 6.0
notch_depth = 4.0

solid_body = Box(channel_width, channel_height, channel_length)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

inner_width = channel_width - 2 * wall_thickness
inner_height = channel_height - wall_thickness
cavity = Pos(0, wall_thickness / 2, 0) * Box(inner_width, inner_height, channel_length)
solid_body = solid_body - cavity

web = Box(web_thickness, channel_height - 2 * wall_thickness, channel_length)
solid_body = solid_body + web

solid_body = fillet(solid_body.edges(), fillet_radius)

for i in range(hole_count):
    z_pos = (i - (hole_count - 1) / 2) * hole_spacing
    hole = Pos(channel_width / 2, 0, z_pos) * Rot(0, 90, 0) * Cylinder(hole_diameter / 2, channel_length)
    solid_body = solid_body - hole

notch = Pos(0, 0, channel_length / 2 - notch_depth / 2) * Box(notch_width, notch_depth, notch_depth)
solid_body = solid_body - notch

part = solid_body
part.name = "channel_with_web"
export_step(part, "output.step")