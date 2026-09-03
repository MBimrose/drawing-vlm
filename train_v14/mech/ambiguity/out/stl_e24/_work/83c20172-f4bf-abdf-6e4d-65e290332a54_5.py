from build123d import *

rail_length = 100.0
rail_width = 50.0
rail_height = 30.0
wall_thickness = 2.0
channel_width = rail_width - 2 * wall_thickness
channel_depth = rail_height - wall_thickness
chamfer_size = 0.5
hole_diameter = 4.0
hole_spacing = 30.0
hole_count = 3

base = Box(rail_length, rail_width, rail_height)
channel = Pos(0, 0, rail_height/2 - channel_depth/2) * Box(channel_width, rail_length, channel_depth)
solid_body = base - channel

chamfer_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.Y)[-4:]
solid_body = chamfer(chamfer_edges, chamfer_size)

for i in range(hole_count):
    x = (i - (hole_count - 1) / 2) * hole_spacing
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(hole_diameter/2, rail_height + 10)

part = solid_body
part.name = "rail_with_channel"
export_step(part, "output.step")