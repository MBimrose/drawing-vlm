from build123d import *

channel_width = 80.0
channel_height = 40.0
channel_length = 100.0
wall_thickness = 5.0
opening_width = 20.0
chamfer_distance = 2.0
hole_diameter = 8.0
grid_hole_diameter = 3.0
grid_rows = 3
grid_cols = 4
grid_spacing = 12.0
pocket_width = 30.0
pocket_height = 20.0
pocket_depth = 3.0

solid = Box(channel_width, channel_length, channel_height)
inner = Pos(wall_thickness/2, 0, 0) * Box(channel_width - wall_thickness, channel_length, channel_height - wall_thickness)
solid = solid - inner

opening = Pos(channel_width/2 - wall_thickness/2, 0, 0) * Box(opening_width, channel_length, channel_height)
solid = solid - opening

top_face = solid.faces().sort_by(Axis.Z)[-1]
solid = chamfer(top_face.edges(), chamfer_distance)

solid = solid - Rot(0, 90, 0) * Cylinder(hole_diameter/2, channel_width)

for i in range(grid_cols):
    for j in range(grid_rows):
        y = (i - (grid_cols-1)/2) * grid_spacing
        z = (j - (grid_rows-1)/2) * grid_spacing
        solid = solid - Pos(-channel_width/2, y, z) * Rot(0, 90, 0) * Cylinder(grid_hole_diameter/2, channel_width)

pocket = Pos(-channel_width/2 + wall_thickness - pocket_depth/2, 0, 0) * Box(pocket_depth, pocket_width, pocket_height)
solid = solid - pocket

part = solid
part.name = "channel"
export_step(part, "output.step")