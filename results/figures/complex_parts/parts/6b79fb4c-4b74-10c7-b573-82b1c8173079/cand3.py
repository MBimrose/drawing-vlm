from build123d import *

channel_width = 80.0
channel_height = 40.0
wall_thickness = 5.0
channel_length = 100.0
pocket_width = 30.0
pocket_length = 20.0
pocket_depth = 10.0
chamfer_size = 2.0
hole_diameter = 8.0
hole_spacing = 12.0
hole_rows = 3
hole_cols = 4

outer = Box(channel_width, channel_length, channel_height)
inner = Pos(wall_thickness/2, 0, 0) * Box(channel_width - wall_thickness, channel_length, channel_height - wall_thickness)
result = outer - inner

pocket = Pos(0, 0, channel_height/2 - pocket_depth/2) * Box(pocket_width, pocket_length, pocket_depth)
result = result - pocket

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

hole_r = hole_diameter / 2
hole_h = channel_width + 20
for i in range(hole_cols):
    for j in range(hole_rows):
        y = (i - (hole_cols - 1) / 2) * hole_spacing
        z = (j - (hole_rows - 1) / 2) * hole_spacing
        result = result - Pos(-channel_width/2, y, z) * Rot(0, 90, 0) * Cylinder(hole_r, hole_h)

part = result
part.name = "channel_with_pocket_and_holes"
export_step(part, "output.step")