from build123d import *

length = 100.0
channel_width = 80.0
channel_height = 40.0
wall_thickness = 5.0
chamfer_size = 2.0
hole_diameter = 8.0
hole_offset_x = wall_thickness / 2.0
hole_offset_z = channel_height / 2.0
pocket_width = 30.0
pocket_height = 20.0
pocket_depth = 3.0
vent_hole_diameter = 3.0
vent_rows = 3
vent_cols = 4
vent_spacing_x = 12.0
vent_spacing_y = 12.0

inner_width = channel_width - wall_thickness
inner_height = channel_height - 2 * wall_thickness
inner_center_x = -channel_width / 2 + wall_thickness + inner_width / 2

result = Box(channel_width, length, channel_height)
inner_cut = Pos(inner_center_x, 0, 0) * Box(inner_width, length, inner_height)
result = result - inner_cut

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

result = result - Pos(hole_offset_x, 0, hole_offset_z - channel_height/2) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, length)

result = result - Pos(-channel_width/2 + pocket_depth/2, 0, 0) * Box(pocket_depth, pocket_width, pocket_height)

for i in range(vent_cols):
    for j in range(vent_rows):
        y = (i - (vent_cols-1)/2) * vent_spacing_x
        z = (j - (vent_rows-1)/2) * vent_spacing_y
        result = result - Pos(-channel_width/2 + wall_thickness/2, y, z) * Rot(0, 90, 0) * Cylinder(vent_hole_diameter/2, wall_thickness)

part = result
part.name = "channel_with_holes"
export_step(part, "output.step")