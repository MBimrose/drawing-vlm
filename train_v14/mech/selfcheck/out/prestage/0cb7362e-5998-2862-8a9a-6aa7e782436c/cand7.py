from build123d import *

length = 80.0
width = 30.0
thickness = 10.0
channel_width = 12.0
channel_depth = 6.0
rib_height = 4.0
rib_width = 6.0
rib_spacing = 15.0
set_screw_diameter = 4.0
set_screw_head_diameter = 7.0
set_screw_head_depth = 2.0
set_screw_offset = 4.0
chamfer_size = 1.0

result = Box(length, width, thickness)

channel = Pos(0, 0, thickness - channel_depth / 2) * Box(length, channel_width, channel_depth)
result = result - channel

num_ribs = int((length - rib_spacing) // rib_spacing) + 1
for i in range(num_ribs):
    x_pos = -length / 2 + rib_spacing / 2 + i * rib_spacing
    rib = Pos(x_pos, 0, -rib_height / 2) * Box(rib_width, width, rib_height)
    result = result + rib

hole_x = length / 2 - set_screw_offset
shaft_hole = Pos(hole_x, 0, 0) * Cylinder(set_screw_diameter / 2, thickness + 10)
result = result - shaft_hole
cbore_hole = Pos(hole_x, 0, -thickness / 2 + set_screw_head_depth / 2) * Cylinder(set_screw_head_diameter / 2, set_screw_head_depth)
result = result - cbore_hole

vertical_edges = result.edges().filter_by(Axis.Z)
result = chamfer(vertical_edges, chamfer_size)

part = result
part.name = "ribbed_plate_with_channel"
export_step(part, "output.step")