from build123d import *

channel_width = 80.0
channel_height = 100.0
channel_depth = 40.0
wall_thickness = 5.0
pocket_width = 30.0
pocket_height = 20.0
pocket_depth = 3.0
chamfer_distance = 2.0
hole_diameter = 8.0
grid_rows = 3
grid_cols = 4
grid_spacing_x = 12.0
grid_spacing_y = 12.0
grid_hole_diameter = 3.0

outer = Box(channel_width, channel_height, channel_depth)
inner_cut = Pos(wall_thickness/2, 0, 0) * Box(channel_width - wall_thickness, channel_height - 2*wall_thickness, channel_depth)
result = outer - inner_cut

pocket = Pos(-channel_width/2 + wall_thickness - pocket_depth/2, 0, 0) * Box(pocket_depth, pocket_width, pocket_height)
result = result - pocket

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_distance)

result = result - Rot(0, 90, 0) * Cylinder(hole_diameter/2, channel_width + 10)

for i in range(grid_cols):
    for j in range(grid_rows):
        y = (i - (grid_cols - 1) / 2) * grid_spacing_x
        z = (j - (grid_rows - 1) / 2) * grid_spacing_y
        result = result - Pos(-channel_width/2, y, z) * Rot(0, 90, 0) * Cylinder(grid_hole_diameter/2, channel_width + 10)

part = result
part.name = "C_channel_with_pockets_and_holes"
export_step(part, "output.step")