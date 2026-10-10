from build123d import *

channel_width = 80.0
channel_length = 100.0
channel_height = 40.0
wall_thickness = 5.0
pocket_width = 30.0
pocket_length = 20.0
pocket_depth = 10.0
pocket_offset_x = 10.0
pocket_offset_y = 10.0
chamfer_size = 2.0
hole_diameter = 8.0
hole_offset_x = 20.0
hole_offset_y = 0.0
grid_hole_diameter = 3.0
grid_rows = 3
grid_cols = 4
grid_spacing_x = 12.0
grid_spacing_y = 12.0
grid_offset_x = 15.0
grid_offset_y = 15.0

solid_body = Box(channel_width, channel_length, channel_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

inner_width = channel_width - wall_thickness
inner_length = channel_length - 2 * wall_thickness
inner_height = channel_height - wall_thickness
inner_cut = Pos(wall_thickness / 2, 0, 0) * Box(inner_width, inner_length, inner_height)
solid_body = solid_body - inner_cut

pocket_x = pocket_offset_x + pocket_width / 2
pocket_y = pocket_offset_y + pocket_length / 2
pocket = Pos(pocket_x, pocket_y, channel_height / 2 - pocket_depth / 2) * Box(pocket_width, pocket_length, pocket_depth)
solid_body = solid_body - pocket

hole = Pos(channel_width / 2, hole_offset_x, hole_offset_y) * Rot(0, 90, 0) * Cylinder(hole_diameter / 2, channel_width + 20)
solid_body = solid_body - hole

for i in range(grid_cols):
    for j in range(grid_rows):
        gx = grid_offset_x + (i - (grid_cols - 1) / 2) * grid_spacing_x
        gy = grid_offset_y + (j - (grid_rows - 1) / 2) * grid_spacing_y
        grid_hole = Pos(-channel_width / 2, gx, gy) * Rot(0, 90, 0) * Cylinder(grid_hole_diameter / 2, channel_width + 20)
        solid_body = solid_body - grid_hole

part = solid_body
part.name = "channel_with_pockets_and_holes"
export_step(part, "output.step")