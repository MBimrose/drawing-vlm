from build123d import *

outer_width = 80.0
outer_height = 40.0
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
vent_spacing_x = 12.0
vent_spacing_y = 12.0

inner_width = outer_width - wall_thickness
inner_height = outer_height - wall_thickness
inner_center_x = -outer_width/2 + wall_thickness + inner_width/2

result = Box(outer_width, length, outer_height)
result = result - Pos(inner_center_x, 0, 0) * Box(inner_width, length, inner_height)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

result = result - Pos(-outer_width/2 + wall_thickness/2, 0, 0) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, wall_thickness)

result = result - Pos(-outer_width/2 + wall_thickness - pocket_depth/2, 0, 0) * Box(pocket_depth, pocket_width, pocket_height)

for i in range(vent_cols):
    for j in range(vent_rows):
        y = (i - (vent_cols-1)/2) * vent_spacing_x
        z = (j - (vent_rows-1)/2) * vent_spacing_y
        result = result - Pos(-outer_width/2 + wall_thickness/2, y, z) * Rot(0, 90, 0) * Cylinder(vent_hole_diameter/2, wall_thickness)

part = result
part.name = "ventilated_channel"
export_step(part, "output.step")