from build123d import *

block_length = 100.0
block_width = 50.0
block_height = 30.0
wall_thickness = 2.0
channel_width = block_width - 2 * wall_thickness
channel_height = block_height - 2 * wall_thickness
rib_thickness = 2.0
rib_height = channel_height - 4.0
hole_diameter = 4.0
hole_spacing = 30.0
chamfer_size = 0.5

solid_body = Pos(0, 0, block_height/2) * Box(block_length, block_width, block_height)
channel_cut = Pos(0, 0, block_height/2) * Box(channel_width, block_length, channel_height)
solid_body = solid_body - channel_cut
rib = Pos(0, 0, wall_thickness + rib_height/2) * Box(block_length, rib_thickness, rib_height)
solid_body = solid_body + rib
for x, y in [(-hole_spacing, 0), (0, 0), (hole_spacing, 0)]:
    solid_body = solid_body - Pos(x, y, block_height/2) * Cylinder(hole_diameter/2, block_height)
vertical_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.Y)[-4:]
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "channel_block_with_rib"
export_step(part, "output.step")