from build123d import *

channel_width = 80.0
channel_height = 40.0
wall_thickness = 5.0
length = 100.0
chamfer_size = 2.0
hole_diameter = 8.0
pocket_width = 30.0
pocket_height = 20.0
pocket_depth = 3.0
vent_hole_diameter = 3.0
vent_rows = 3
vent_cols = 4
vent_spacing = 12.0

outer = Box(channel_width, length, channel_height)
inner = Pos(wall_thickness, 0, 0) * Box(channel_width - 2 * wall_thickness, length, channel_height - wall_thickness)
channel = outer - inner

top_face = channel.faces().sort_by(Axis.Z)[-1]
channel = chamfer(top_face.edges(), chamfer_size)

channel = channel - Pos(-channel_width/2 + wall_thickness/2, 0, 0) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, wall_thickness + 1)

channel = channel - Pos(-channel_width/2 + wall_thickness - pocket_depth/2, 0, 0) * Box(pocket_depth, pocket_width, pocket_height)

for i in range(vent_cols):
    for j in range(vent_rows):
        y = (i - (vent_cols - 1) / 2) * vent_spacing
        z = (j - (vent_rows - 1) / 2) * vent_spacing
        channel = channel - Pos(-channel_width/2 + wall_thickness/2, y, z) * Rot(0, 90, 0) * Cylinder(vent_hole_diameter/2, wall_thickness + 1)

part = channel
part.name = "channel_with_holes"
export_step(part, "output.step")