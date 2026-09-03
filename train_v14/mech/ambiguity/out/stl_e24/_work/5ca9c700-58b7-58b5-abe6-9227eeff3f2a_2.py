from build123d import *

outer_width = 80.0
outer_height = 60.0
length = 100.0
channel_width = 20.0
channel_depth = 15.0
hole_diameter = 8.0
chamfer_size = 1.0

base = Box(outer_width, outer_height, length)
channel = Pos(outer_width/2 - channel_width/2, 0, 0) * Box(channel_width, channel_depth, length)
solid_body = base - channel
solid_body = solid_body - Cylinder(hole_diameter/2, length)
vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "channel_block"
export_step(part, "output.step")