from build123d import *

outer_length = 100.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
channel_width = 30.0
channel_height = 20.0
groove_width = 10.0
groove_depth = 2.0
chamfer_size = 0.5
hole_diameter = 4.0
hole_spacing = 30.0
hole_count = 3

base = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
channel = Pos(0, 0, channel_height/2) * Box(channel_width, outer_length, channel_height)
result = base - channel

groove = Pos(0, 0, outer_height - groove_depth/2) * Box(groove_width, outer_length, groove_depth)
result = result - groove

z_edges = result.edges().filter_by(Axis.Z)
pos_x_edges = [e for e in z_edges if e.center().X > 0]
result = chamfer(pos_x_edges, chamfer_size)

for i in range(hole_count):
    x = (i - (hole_count-1)/2) * hole_spacing
    hole = Pos(x, 0, outer_height/2) * Cylinder(hole_diameter/2, outer_height)
    result = result - hole

part = result
part.name = "channel_block"
export_step(part, "output.step")