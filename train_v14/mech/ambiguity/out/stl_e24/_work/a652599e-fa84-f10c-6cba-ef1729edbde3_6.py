from build123d import *

block_length = 80.0
block_width = 40.0
block_height = 20.0
corner_fillet_radius = 5.0
central_hole_diameter = 12.0
blind_hole_diameter = 4.2
blind_hole_depth = 10.0
blind_hole_offset = 15.0
rib_width = 5.0
rib_height = 10.0
rib_spacing = 20.0
chamfer_distance = 1.0

solid_body = Box(block_length, block_width, block_height)

y_edges = solid_body.edges().filter_by(Axis.Y)
solid_body = fillet(y_edges, corner_fillet_radius)

solid_body = solid_body - Pos(0, 0, block_height/2) * Cylinder(central_hole_diameter/2, block_height)

blind_positions = [
    (blind_hole_offset, blind_hole_offset),
    (-blind_hole_offset, blind_hole_offset),
    (blind_hole_offset, -blind_hole_offset),
    (-blind_hole_offset, -blind_hole_offset),
]
for x, y in blind_positions:
    solid_body = solid_body - Pos(x, y, block_height/2 - blind_hole_depth/2) * Cylinder(blind_hole_diameter/2, blind_hole_depth)

rib_count = int((block_length - 2 * blind_hole_offset) // rib_spacing) + 1
for i in range(rib_count):
    x_pos = -block_length/2 + blind_hole_offset + i * rib_spacing
    rib = Pos(x_pos, 0, rib_height/2) * Box(rib_width, block_width, rib_height)
    solid_body = solid_body + rib

z_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(z_edges, chamfer_distance)

part = solid_body
part.name = "ribbed_block_with_holes"
export_step(part, "output.step")