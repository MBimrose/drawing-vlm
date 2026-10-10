from build123d import *

channel_width = 80.0
channel_height = 40.0
wall_thickness = 5.0
length = 100.0
pocket_width = 30.0
pocket_height = 20.0
pocket_depth = 10.0
chamfer_size = 2.0
hole_diameter = 8.0
vent_hole_diameter = 3.0
vent_rows = 3
vent_cols = 4
vent_spacing_x = 12.0
vent_spacing_y = 10.0

outer = Box(channel_width, length, channel_height)
inner = Pos(wall_thickness/2, 0, 0) * Box(channel_width - wall_thickness, length, channel_height - 2*wall_thickness)
result = outer - inner

pocket = Pos(0, 0, channel_height/2 - pocket_depth/2) * Box(pocket_width, pocket_height, pocket_depth)
result = result - pocket

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

result = result - Pos(-channel_width/2, 0, 0) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, length)

for i in range(vent_cols):
    for j in range(vent_rows):
        y = (i - (vent_cols - 1) / 2) * vent_spacing_x
        z = (j - (vent_rows - 1) / 2) * vent_spacing_y
        result = result - Pos(-channel_width/2, y, z) * Rot(0, 90, 0) * Cylinder(vent_hole_diameter/2, length)

part = result
part.name = "C_channel_with_pocket_and_holes"
export_step(part, "output.step")