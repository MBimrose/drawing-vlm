from build123d import *

block_length = 100.0
block_width = 50.0
block_height = 30.0
channel_width = 20.0
channel_depth = 15.0
wall_thickness = 2.0
chamfer_size = 0.5
hole_diameter = 4.0
hole_spacing = 30.0
hole_count = 3

base = Pos(0, 0, block_height/2) * Box(block_length, block_width, block_height)

channel_cut = Pos(0, 0, block_height - channel_depth/2) * Box(channel_width, block_width, channel_depth)
base = base - channel_cut

thin_walls = offset(base, amount=-wall_thickness, openings=base.faces())

z_edges = thin_walls.edges().filter_by(Axis.Z)
chamfer_edges = [e for e in z_edges if e.center().Y > 0]
thin_walls = chamfer(chamfer_edges, chamfer_size)

for i in range(hole_count):
    x = (i - (hole_count - 1) / 2) * hole_spacing
    thin_walls = thin_walls - Pos(x, 0, block_height/2) * Cylinder(hole_diameter/2, block_height)

part = thin_walls
part.name = "channel_block"
export_step(part, "output.step")