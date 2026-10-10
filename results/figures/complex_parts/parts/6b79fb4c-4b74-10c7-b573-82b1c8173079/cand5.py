from build123d import *

channel_width = 80.0
channel_height = 40.0
wall_thickness = 5.0
length = 100.0
chamfer_size = 2.0
hole_diameter = 8.0
hole_offset_x = wall_thickness / 2.0
hole_offset_z = channel_height / 2.0
grid_rows = 3
grid_cols = 4
grid_spacing_x = 12.0
grid_spacing_z = 12.0
grid_hole_diameter = 3.0
pocket_width = 30.0
pocket_depth = 2.0

outer = Box(channel_width, length, channel_height)
inner = Pos(wall_thickness / 2.0, 0, 0) * Box(channel_width - wall_thickness, length, channel_height - 2 * wall_thickness)
result = outer - inner

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

result = result - Pos(hole_offset_x, 0, hole_offset_z - channel_height / 2.0) * Rot(0, 90, 0) * Cylinder(hole_diameter / 2.0, channel_width)

for i in range(grid_cols):
    for j in range(grid_rows):
        y = (i - (grid_cols - 1) / 2.0) * grid_spacing_x
        z = (j - (grid_rows - 1) / 2.0) * grid_spacing_z
        result = result - Pos(-channel_width / 2.0 + wall_thickness / 2.0, y, z) * Rot(0, 90, 0) * Cylinder(grid_hole_diameter / 2.0, wall_thickness)

result = result - Pos(0, 0, channel_height / 2.0 - pocket_depth / 2.0) * Box(pocket_width, pocket_width, pocket_depth)

part = result
part.name = "C_channel_with_holes"
export_step(part, "output.step")