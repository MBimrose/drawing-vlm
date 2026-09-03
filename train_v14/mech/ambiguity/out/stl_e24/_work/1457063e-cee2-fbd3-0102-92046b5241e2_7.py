from build123d import *
import math

channel_length = 100.0
channel_width = 60.0
channel_height = 30.0
wall_thickness = 2.0
rib_thickness = 2.0
rib_height = 10.0
rib_spacing = 15.0
hole_diameter = 5.0
hole_count = 7
chamfer_size = 0.8

base = Pos(0, 0, channel_height/2) * Box(channel_length, channel_width, channel_height)
left_rib = Pos(-channel_length/2 + rib_height/2, 0, channel_height/2) * Box(rib_height, channel_width, channel_height)
right_rib = Pos(channel_length/2 - rib_height/2, 0, channel_height/2) * Box(rib_height, channel_width, channel_height)

solid_body = base + left_rib + right_rib
solid_body = offset(solid_body, amount=-wall_thickness)

left_face = solid_body.faces().sort_by(Axis.X)[0]
solid_body = chamfer(left_face.edges(), chamfer_size)

hole_spacing = channel_length / (hole_count + 1)
for i in range(hole_count):
    x = -channel_length/2 + hole_spacing * (i + 1)
    solid_body = solid_body - Pos(x, 0, channel_height/2) * Cylinder(hole_diameter/2, channel_height + 20)

part = solid_body
part.name = "channel_with_ribs"
export_step(part, "output.step")