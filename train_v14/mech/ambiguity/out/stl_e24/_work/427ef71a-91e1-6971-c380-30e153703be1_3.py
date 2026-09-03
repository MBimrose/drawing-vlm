from build123d import *

socket_width = 50.0
socket_depth = 60.0
socket_height = 30.0
wall_thickness = 5.0
split_gap = 2.0
chamfer_size = 1.0

outer_width = socket_width + 2 * wall_thickness
outer_depth = socket_depth + 2 * wall_thickness
inner_height = socket_height - wall_thickness

outer = Pos(0, 0, socket_height/2) * Box(outer_width, outer_depth, socket_height)
inner = Pos(0, 0, wall_thickness + inner_height/2) * Box(socket_width, socket_depth, inner_height)
socket_body = outer - inner

split_cut = Pos(0, -outer_depth/2 + wall_thickness/2, 0) * Box(split_gap, wall_thickness, socket_height)
socket_split = socket_body - split_cut

bottom_front_edges = socket_split.edges().filter_by(Axis.X).sort_by(Axis.Z)[:1]
result = chamfer(bottom_front_edges, chamfer_size)

part = result
part.name = "XMountSocket"
export_step(part, "output.step")